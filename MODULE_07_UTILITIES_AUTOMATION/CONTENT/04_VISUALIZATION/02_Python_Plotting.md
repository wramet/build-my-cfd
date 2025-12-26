# 📊 Python Plotting Integration (การบูรณาการการพล็อตด้วย Python)

**ภาพรวม (Overview)**: เฟรมเวิร์กการพล็อตข้อมูลด้วย Python ระดับมืออาชีพสำหรับการวิเคราะห์ CFD คุณภาพสูงเพื่อการตีพิมพ์ (Publication-quality) และรายงานทางเทคนิค

> [!INFO] ทำไมต้องใช้ Python สำหรับ CFD Visualization?
> แม้ว่า ParaView จะเหมาะสำหรับการสร้างภาพ 3D แต่ Python ให้ความยืดหยุ่นในการวิเคราะห์ข้อมูลเชิงปริมาณ (Quantitative Analysis) การสร้างกราฟที่ปรับแต่งได้ และการทำงานอัตโนมัติ (Automation) สำหรับชุดข้อมูลขนาดใหญ่

---

## 1. บทนำสู่การพล็อตด้วย Python (Introduction)

### 1.1 ข้อดีของ Python Visualization Ecosystem

ในขณะที่ ParaView มีความโดดเด่นในการแสดงภาพ 3 มิติ (3D Visualization) แต่สำหรับการวิเคราะห์ข้อมูลเชิงปริมาณ (Quantitative Analysis) 2 มิติ ไลบรารีของ Python เช่น `Matplotlib`, `Seaborn`, และ `Plotly` เป็นมาตรฐานอุตสาหกรรมที่ให้:

- **การควบคุมคุณภาพระดับสูง**: ปรับแต่งฟอนต์, ขนาดเส้น และจานสีตามมาตรฐานวารสารวิชาการ
- **การวิเคราะห์ข้อมูลทางสถิติ**: การทำ Curve Fitting, การคำนวณค่าเฉลี่ย และการวิเคราะห์แนวโน้มจากข้อมูล `postProcessing`
- **ระบบอัตโนมัติ (Automation)**: สร้างกราฟเปรียบเทียบจากกรณีศึกษาหลายสิบกรณีได้ในคลิกเดียว

### 1.2 ขั้นตอนการทำงานของการพล็อต (Plotting Workflow)

```mermaid
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000

A[Results]:::explicit --> B[postProcess Data]:::explicit
B --> C[Python Load]:::implicit
C --> D[Analysis]:::implicit
D --> E[Plotting]:::implicit
E --> F[Report PDF]:::implicit
```
> **Figure 1:** แผนภูมิขั้นตอนการทำงานสำหรับการวิเคราะห์และพล็อตข้อมูลด้วย Python ตั้งแต่การสกัดข้อมูลจาก `postProcessing` การโหลดข้อมูลด้วย Pandas/NumPy การวิเคราะห์ทางสถิติ ไปจนถึงการสร้างกราฟด้วย Matplotlib และการจัดทำรายงานระดับมืออาชีพ

![[plotting_workflow_visual.png]]
> **รูปที่ 1.1:** วงจรการทำงานของการพล็อตและวิเคราะห์ข้อมูล: จากการสกัดข้อมูลดิบไปจนถึงการจัดทำรูปเล่มรายงานทางเทคนิค

---

## 2. การติดตั้งและการเตรียมความพร้อม (Setup and Preparation)

### 2.1 การติดตั้ง Python Environment

สำหรับการวิเคราะห์ข้อมูล CFD แนะนำให้ใช้ Anaconda หรือ Miniconda:

```bash
# NOTE: Synthesized by AI - Verify parameters
# Create environment for CFD Visualization
conda create -n cfd-vis python=3.11

# Activate environment
conda activate cfd-vis

# Install main libraries
conda install -c conda-forge matplotlib numpy pandas scipy

# Install additional libraries for visualization
pip install seaborn plotly pyvista kaleido
```

> **📂 Source:** OpenFOAM postProcessing directory structure  
> **คำอธิบาย (Explanation):** คำสั่งนี้สร้าง environment เฉพาะสำหรับการทำ CFD visualization เพื่อหลีกเลี่ยงปัญหาความขัดแย้งของ dependencies การใช้ conda-forge channel ให้แพ็กเกจที่อัปเดตกว่า default channel  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Environment Isolation**: แยก dependencies ของแต่ละโปรเจกต์
> - **Conda vs Pip**: conda สำหรับ binary packages, pip สำหรับ pure Python packages
> - **CFD-Specific Libraries**: PyVista สำหรับ 3D mesh visualization, Kaleido สำหรับ static export จาก Plotly

### 2.2 การติดตั้ง PyFoam

PyFoam เป็น Python library สำหรับทำงานร่วมกับ OpenFOAM:

```bash
# NOTE: Synthesized by AI - Verify parameters
pip install PyFoam
# Or use conda
conda install -c conda-forge pyfoam
```

> **📂 Source:** PyFoam documentation  
> **คำอธิบาย (Explanation):** PyFoam ให้ API สำหรับการจัดการ OpenFOAM cases อัตโนมัติ รวมถึงการอ่านเขียน OpenFOAM dictionary files และการ monitor solver execution  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Dictionary Parser**: แปลง OpenFOAM dict format เป็น Python objects
> - **Solver Wrapper**: Run OpenFOAM solvers จาก Python scripts
> - **Case Management**: Automate parameter studies and mesh generation

### 2.3 การตั้งค่า Matplotlib สำหรับการตีพิมพ์

ไฟล์ `matplotlibrc` หรือการตั้งค่าใน script:

```python
# NOTE: Synthesized by AI - Verify parameters
import matplotlib.pyplot as plt
import numpy as np

# Professional settings for academic journals
plt.rcParams.update({
    # Fonts and text sizes
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 12,
    "axes.labelsize": 14,
    "axes.titlesize": 16,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,

    # Figure quality
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.format": "pdf",
    "savefig.bbox": "tight",

    # Lines and colors
    "lines.linewidth": 1.5,
    "lines.markersize": 6,
    "axes.linewidth": 1.0,

    # Colormap
    "image.cmap": "viridis",

    # Grid
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})
```

> **📂 Source:** Matplotlib rcParams documentation  
> **คำอธิบาย (Explanation):** การตั้งค่า rcParams ช่วยให้ทุกกราฟใน session มี style สม่ำเสมอ ค่า DPI 300 เป็นมาตรฐานสำหรับ printing และ PDF format รักษาคุณภาพเวกเตอร์  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Publication Standards**: Serif fonts (Times New Roman) สำหรับ journal articles
> - **Vector Graphics**: PDF/SVG รักษาความคมชัดทุกขนาด
> - **Consistent Styling**: rcParams ทำให้ style สม่ำเสมอทั้ง project
> - **Color Accessibility**: viridis colormap สามารถพิมพ์ขาวด้ายได้

---

## 3. การอ่านข้อมูลจาก OpenFOAM (Reading OpenFOAM Data)

### 3.1 รูปแบบข้อมูลจาก postProcessing

OpenFOAM ส่งออกข้อมูลหลายรูปแบบ:

**3.1.1 ไฟล์ CSV จาก `sample` Utility:**

```plaintext
postProcessing/surfaces/0.5/centreLine_U.csv
```

**3.1.2 ไฟล์จาก `probes`:**

```plaintext
postProcessing/probes/0.5/U
```

**3.1.3 ไฟล์จาก `forces`:**

```plaintext
postProcessing/forces/0/forces.dat
```

> **📂 Source:** OpenFOAM postProcessing directory  
> **คำอธิบาย (Explanation):** OpenFOAM utilities เขียนข้อมูลไปยัง `postProcessing` subdirectory โครงสร้างคือ `postProcessing/<functionName>/<time>/<filename>`  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Time Directories**: แต่ละ time folder มีข้อมูลเฉพาะ time step นั้น
> - **ASCII vs Binary**: สามารถเลือก format ใน `controlDict`
> - **Output Frequency**: ควบคุมด้วย `writeControl` และ `writeInterval`

### 3.2 การอ่านข้อมูล CSV ด้วย Pandas

```python
# NOTE: Synthesized by AI - Verify parameters
import pandas as pd
import numpy as np

def read_openfoam_csv(filepath):
    """
    Read CSV file from OpenFOAM sample utility

    Parameters:
    -----------
    filepath : str
        Path to CSV file

    Returns:
    --------
    pandas.DataFrame
        Loaded data
    """
    # Read file (skip comment lines starting with #)
    df = pd.read_csv(filepath, comment='#', skipinitialspace=True)

    return df

# Example usage
velocity_data = read_openfoam_csv('postProcessing/surfaces/0.5/centreLine_U.csv')
print(velocity_data.head())
```

> **📂 Source:** OpenFOAM sampleDict output format  
> **คำอธิบาย (Explanation):** Pandas `read_csv` พร้อม `comment='#'` จะข้าม header lines ของ OpenFOAM อัตโนมัติ ซึ่งเริ่มต้นด้วย `#`  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Comment Stripping**: OpenFOAM เขียน metadata เป็น comment lines
> - **DataFrame Structure**: Pandas จัดเก็บข้อมูลเป็น tabular format
> - **Vector Components**: OpenFOAM output เป็น `(Ux Uy Uz)` columns

### 3.3 การอ่านข้อมูลจาก probes

```python
# NOTE: Synthesized by AI - Verify parameters
def read_probes_data(filepath):
    """
    Read data from probes utility

    Parameters:
    -----------
    filepath : str
        Path to probes file

    Returns:
    --------
    dict
        Dictionary of arrays for each probe
    """
    data = {}
    current_probe = []
    probe_count = 0

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()

            # Start new probe
            if line.startswith('# Probe'):
                if current_probe:
                    data[f'probe_{probe_count}'] = np.array(current_probe)
                    current_probe = []
                    probe_count += 1

            # Read data (skip comments and empty lines)
            elif line and not line.startswith('#'):
                values = [float(x) for x in line.split()]
                current_probe.append(values)

        # Last probe
        if current_probe:
            data[f'probe_{probe_count}'] = np.array(current_probe)

    return data

# Example usage
probes_data = read_probes_data('postProcessing/probes/0.5/U')
```

> **📂 Source:** OpenFOAM probes function output  
> **คำอธิบาย (Explanation):** Probes utility เขียนข้อมูลหลายจุดวัดในไฟล์เดียว โดยแบ่งด้วย comment headers แต่ละ probe มี time history  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Probe Locations**: กำหนดใน `probesDict` หรือ via `sampleDict`
> - **Time Series**: แต่ละ probe เก็บ temporal data
> - **Multi-Point Monitoring**: Monitor หลายจุดพร้อมกัน

### 3.4 การอ่านข้อมูล Forces

```python
# NOTE: Synthesized by AI - Verify parameters
def read_forces_data(filepath):
    """
    Read forces data from forces utility

    Parameters:
    -----------
    filepath : str
        Path to forces.dat file

    Returns:
    --------
    pandas.DataFrame
        Forces data with column names
    """
    # Read file (skip header with #)
    df = pd.read_csv(filepath,
                     sep='\t',
                     comment='#',
                     names=['Time',
                            'Fx_p', 'Fy_p', 'Fz_p',
                            'Fx_viscous', 'Fy_viscous', 'Fz_viscous',
                            'Fx_total', 'Fy_total', 'Fz_total',
                            'Mx', 'My', 'Mz'])

    return df

# Example usage
forces_data = read_forces_data('postProcessing/forces/0/forces.dat')

# Calculate Drag and Lift Coefficients
rho = 1.225      # kg/m³
U_inf = 10.0     # m/s
A_ref = 1.0      # m² (reference area)

# Drag coefficient (assuming drag in x-direction)
Cd = 2 * forces_data['Fx_total'] / (rho * U_inf**2 * A_ref)

# Lift coefficient (assuming lift in y-direction)
Cl = 2 * forces_data['Fy_total'] / (rho * U_inf**2 * A_ref)
```

> **📂 Source:** OpenFOAM forces function  
> **คำอธิบาย (Explanation):** Forces utility คำนวณ pressure และ viscous forces บน patches ต่างๆ สำหรับ aerodynamic/hydrodynamic analysis  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Force Decomposition**: Total = Pressure + Viscous components
> - **Coefficient Normalization**: $C = F / (0.5 \rho U^2 A)$
> - **Moment Calculation**: Torque around center of rotation
> - **Reference Values**: ต้องระบุใน `forcesDict`

---

## 4. การวิเคราะห์ชั้นขอบเขต (Boundary Layer Analysis)

### 4.1 รากฐานทางทฤษฎี (Theoretical Foundation)

การวิเคราะห์โปรไฟล์ความเร็ว $U(y)$ ใกล้ผนังมีความสำคัญอย่างยิ่งต่อการตรวจสอบความถูกต้องของการจำลอง โดยใช้พารามิเตอร์เชิงปริพันธ์ (Integral Parameters):

**ความหนากระจัด (Displacement Thickness):**
$$\delta^* = \int_{0}^{\infty} \left(1 - \frac{U}{U_{\infty}}\right) \,\mathrm{d}y \tag{1}$$

**ความหนาโมเมนตัม (Momentum Thickness):**
$$\theta = \int_{0}^{\infty} \frac{U}{U_{\infty}} \left(1 - \frac{U}{U_{\infty}}\right) \,\mathrm{d}y \tag{2}$$

**ปัจจัยรูปร่าง (Shape Factor):**
$$H = \frac{\delta^*}{\theta} \tag{3}$$

### 4.2 การตีความค่า Shape Factor ($H$)

ค่า $H$ ช่วยให้วิศวกรระบุสถานะของการไหลได้อย่างรวดเร็ว:

| ค่า $H$ | สถานะการไหล | คำอธิบาย |
|---|---|---|
| **$H \approx 2.59$** | Laminar (Blasius) | การไหลแบบ Laminar บนแผ่นเรียบ |
| **$H \approx 1.3 - 1.5$** | Turbulent | การไหลแบบ Turbulent ที่มีการผสม |
| **$H > 2.6$** | Separation | การแยกตัวของการไหล (Flow Separation) |
| **$1.1 < H < 1.3$** | Relaminarization | การกลับไปเป็น Laminar |

![[shape_factor_interpretation_visual.png]]
> **รูปที่ 4.1:** การตีความพารามิเตอร์ Shape Factor ($H$) ในการระบุลักษณะการไหล

### 4.3 การคำนวณ Boundary Layer Parameters ด้วย Python

```python
# NOTE: Synthesized by AI - Verify parameters
import numpy as np
from scipy.integrate import simpson

def calculate_boundary_layer_params(y, U, U_inf):
    """
    Calculate boundary layer parameters

    Parameters:
    -----------
    y : numpy.ndarray
        Normal distance from wall [m]
    U : numpy.ndarray
        x-velocity at each y position [m/s]
    U_inf : float
        Freestream velocity [m/s]

    Returns:
    --------
    dict
        Dictionary of boundary layer parameters:
        - delta_star: Displacement thickness
        - theta: Momentum thickness
        - H: Shape factor
        - delta_99: Boundary layer thickness (99% criterion)
    """

    # Normalize velocity
    U_norm = U / U_inf

    # Calculate displacement thickness (Simpson's rule)
    delta_star = simpson(1 - U_norm, y)

    # Calculate momentum thickness
    theta = simpson(U_norm * (1 - U_norm), y)

    # Calculate shape factor
    H = delta_star / theta

    # Calculate boundary layer thickness (99% criterion)
    delta_99 = np.interp(0.99 * U_inf, U, y)

    return {
        'delta_star': delta_star,
        'theta': theta,
        'H': H,
        'delta_99': delta_99
    }

# Example usage
y = np.array([0.0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1])  # m
U = np.array([0.0, 0.5, 1.2, 3.5, 6.0, 8.5, 9.8, 10.0])         # m/s
U_inf = 10.0  # m/s

bl_params = calculate_boundary_layer_params(y, U, U_inf)

print(f"Displacement Thickness (δ*): {bl_params['delta_star']:.6f} m")
print(f"Momentum Thickness (θ):     {bl_params['theta']:.6f} m")
print(f"Shape Factor (H):           {bl_params['H']:.3f}")
print(f"Boundary Layer Thickness (δ99): {bl_params['delta_99']:.4f} m")
```

> **📂 Source:** Boundary layer theory fundamentals  
> **คำอธิบาย (Explanation):** Simpson's rule ให้ความแม่นยำสูงกว่า trapezoidal rule สำหรับ numerical integration ของ velocity profiles  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Integral Parameters**: สรุป profile ทั้งหมดด้วยตัวเลขเดียว
> - **Displacement Effect**: δ* แทนการเบี่ยงเบน streamlines
> - **Momentum Loss**: θ แทนการสูญเสียโมเมนตัม
> - **Flow Regime Indicator**: H บอกสถานะ laminar/turbulent/separated

### 4.4 การพล็อต Velocity Profile

```python
# NOTE: Synthesized by AI - Verify parameters
import matplotlib.pyplot as plt

def plot_velocity_profile(y, U, U_inf, bl_params, ax=None):
    """
    Plot velocity profile with boundary layer parameters

    Parameters:
    -----------
    y : numpy.ndarray
        Normal distance from wall [m]
    U : numpy.ndarray
        x-velocity [m/s]
    U_inf : float
        Freestream velocity [m/s]
    bl_params : dict
        Boundary layer parameters from calculate_boundary_layer_params()
    ax : matplotlib.axes.Axes, optional
        Axes object for plotting
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    # Plot velocity profile
    ax.plot(U, y * 1000, 'b-', linewidth=2, label='Velocity Profile')
    ax.fill_betweenx(y * 1000, 0, U, alpha=0.2)

    # Mark U_inf
    ax.axvline(U_inf, color='r', linestyle='--', alpha=0.5, label=f'$U_\\infty$ = {U_inf} m/s')

    # Mark boundary layer thickness
    ax.axhline(bl_params['delta_99'] * 1000, color='g', linestyle=':',
               label=f'$\\delta_{{99}}$ = {bl_params["delta_99"]*1000:.2f} mm')

    # Labels and title
    ax.set_xlabel('$U_x$ [m/s]', fontsize=14)
    ax.set_ylabel('$y$ [mm]', fontsize=14)
    ax.set_title('Boundary Layer Velocity Profile', fontsize=16)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)

    # Add parameter text box
    textstr = f'$\\delta^*$ = {bl_params["delta_star"]*1000:.3f} mm\n'
    textstr += f'$\\theta$ = {bl_params["theta"]*1000:.3f} mm\n'
    textstr += f'$H$ = {bl_params["H"]:.3f}'

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    ax.set_xlim(0, U_inf * 1.1)

    return ax

# Example usage
fig, ax = plt.subplots(figsize=(10, 6))
plot_velocity_profile(y, U, U_inf, bl_params, ax=ax)
plt.tight_layout()
plt.savefig('boundary_layer_profile.pdf', dpi=300)
plt.show()
```

> **📂 Source:** Velocity profile visualization standards  
> **คำอธิบาย (Explanation):** การพล็อต $U$ บน x-axis และ $y$ บน y-axis เป็น convention มาตรฐานสำหรับ boundary layer profiles  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Profile Orientation**: Horizontal velocity กับ vertical distance
> - **Annotation**: Mark U∞ และ δ99 สำหรับ context
> - **Fill Between**: Visualize velocity deficit
> - **Text Box**: แสดงค่าพารามิเตอร์สำคัญ

### 4.5 Law of the Wall Analysis

สำหรับการวิเคราะห์ Turbulent Boundary Layer ในรูปแบบ Non-dimensional:

**สมการพื้นฐาน:**

$$y^+ = \frac{y u_\tau}{\nu}, \quad u^+ = \frac{U}{u_\tau} \tag{4}$$

โดยที่ $u_\tau$ คือ Friction velocity:
$$u_\tau = \sqrt{\frac{\tau_w}{\rho}} \tag{5}$$

**Viscous Sublayer ($y^+ < 5$):**
$$u^+ = y^+ \tag{6}$$

**Log-law Region ($y^+ > 30$):**
$$u^+ = \frac{1}{\kappa} \ln(y^+) + B \tag{7}$$

โดยที่ $\kappa \approx 0.41$ (von Kármán constant) และ $B \approx 5.0$

```python
# NOTE: Synthesized by AI - Verify parameters
def plot_law_of_the_wall(y, U, nu, rho, tau_w, ax=None):
    """
    Plot Law of the Wall

    Parameters:
    -----------
    y : numpy.ndarray
        Distance from wall [m]
    U : numpy.ndarray
        Velocity [m/s]
    nu : float
        Kinematic viscosity [m²/s]
    rho : float
        Density [kg/m³]
    tau_w : float
        Wall shear stress [Pa]
    ax : matplotlib.axes.Axes, optional
        Axes object
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))

    # Calculate friction velocity
    u_tau = np.sqrt(tau_w / rho)

    # Calculate non-dimensional parameters
    y_plus = y * u_tau / nu
    u_plus = U / u_tau

    # Plot simulation data
    ax.semilogx(y_plus, u_plus, 'bo', label='OpenFOAM Data', alpha=0.6)

    # Viscous sublayer (u+ = y+)
    y_sublayer = np.logspace(-1, np.log10(5), 50)
    u_sublayer = y_sublayer
    ax.plot(y_sublayer, u_sublayer, 'r-', linewidth=2, label='Viscous Sublayer ($u^+ = y^+$)')

    # Log-law region
    kappa = 0.41
    B = 5.0
    y_log = np.logspace(np.log10(30), 3, 100)
    u_log = (1.0 / kappa) * np.log(y_log) + B
    ax.plot(y_log, u_log, 'g-', linewidth=2,
            label=f'Log Law ($\\kappa$={kappa}, B={B})')

    # Buffer layer marker
    ax.axvspan(5, 30, alpha=0.2, color='yellow', label='Buffer Layer')

    # Labels
    ax.set_xlabel('$y^+$', fontsize=14)
    ax.set_ylabel('$u^+$', fontsize=14)
    ax.set_title('Law of the Wall', fontsize=16)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.1, 1000)
    ax.set_ylim(0, 30)

    return ax
```

> **📂 Source:** Turbulent boundary layer theory  
> **คำอธิบาย (Explanation):** Law of the wall เป็น universal profile สำหรับ turbulent boundary layers ใช้ validate turbulence models  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Wall Units**: y+ และ u+ ทำให้ profile non-dimensional
> - **Three Layers**: Viscous sublayer, buffer layer, log-law region
> - **Universal Constants**: κ และ B ค่าคงที่ทั่วไป
> - **Model Validation**: เปรียบเทียบ CFD กับ theory/experiment

---

## 5. การระบุลักษณะกระแสตาม (Wake Characterization)

### 5.1 ฟิสิกส์ของกระแสตาม (Wake Physics)

บริเวณ Wake ด้านหลังวัตถุมีการสูญเสียโมเมนตัมซึ่งสามารถวิเคราะห์ได้ผ่าน:

**การขาดดุลความเร็ว (Velocity Deficit):**
$$\Delta U(x, y) = U_{\infty} - U(x, y) \tag{8}$$

**สัมประสิทธิ์การลดลงของความเร็ว (Velocity Deficit Coefficient):**
$$C_d(x, y) = \frac{\Delta U(x, y)}{U_{\infty}} \tag{9}$$

**การลดลงของความดัน (Pressure Recovery):**

วิเคราะห์การฟื้นตัวของความดันตามแนวแกนกลางของ Wake (Centerline Recovery) เพื่อระบุระยะที่การไหลกลับมาเสถียรอีกครั้ง

**ความกว้างของ Wake (Wake Width):**

กำหนดโดยระยะห่างระหว่างจุดที่ความเร็วถึง 50% ของการขาดดุลสูงสุด:
$$w_{0.5}(x) = y_2 - y_1 \quad \text{where} \quad U(y_i) = U_{\infty} - 0.5 \Delta U_{\max} \tag{10}$$

### 5.2 การวิเคราะห์ Wake Profile

```python
# NOTE: Synthesized by AI - Verify parameters
def analyze_wake_profile(y_coords, U_data, U_inf, x_position):
    """
    Analyze wake profile at specified x position

    Parameters:
    -----------
    y_coords : numpy.ndarray
        Vertical coordinates [m]
    U_data : numpy.ndarray
        x-velocity at specified x position [m/s]
    U_inf : float
        Freestream velocity [m/s]
    x_position : float
        Analysis x position [m]

    Returns:
    --------
    dict
        Wake parameters:
        - deficit_max: Maximum velocity deficit
        - deficit_profile: Velocity deficit profile
        - wake_width: Wake width (50% criterion)
        - centerline_velocity: Velocity at wake centerline
    """

    # Calculate velocity deficit
    deficit = U_inf - U_data
    deficit_max = np.max(deficit)

    # Find centerline position (maximum deficit)
    centerline_idx = np.argmax(deficit)
    centerline_velocity = U_data[centerline_idx]
    centerline_y = y_coords[centerline_idx]

    # Calculate wake width (50% criterion)
    half_deficit = deficit_max / 2.0

    # Find points where deficit = 0.5 * deficit_max
    from scipy.interpolate import interp1d

    # Interpolate for accurate positions
    f = interp1d(y_coords, deficit - half_deficit, kind='linear')

    # Find intersection points (root finding)
    try:
        # Left of centerline
        y_left = y_coords[:centerline_idx]
        deficit_left = deficit[:centerline_idx] - half_deficit
        if np.any(deficit_left > 0) and np.any(deficit_left < 0):
            y1 = np.interp(0, deficit_left[::-1], y_left[::-1])
        else:
            y1 = y_coords[0]

        # Right of centerline
        y_right = y_coords[centerline_idx:]
        deficit_right = deficit[centerline_idx:] - half_deficit
        if np.any(deficit_right > 0) and np.any(deficit_right < 0):
            y2 = np.interp(0, deficit_right, y_right)
        else:
            y2 = y_coords[-1]

        wake_width = y2 - y1
    except:
        wake_width = np.nan

    return {
        'x_position': x_position,
        'deficit_max': deficit_max,
        'deficit_max_coefficient': deficit_max / U_inf,
        'deficit_profile': deficit,
        'wake_width': wake_width,
        'centerline_velocity': centerline_velocity,
        'centerline_y': centerline_y
    }

# Example usage
y_coords = np.linspace(-0.5, 0.5, 100)
U_data = 10.0 - 3.0 * np.exp(-(y_coords / 0.15)**2)  # Gaussian wake profile
U_inf = 10.0
x_position = 2.0

wake_params = analyze_wake_profile(y_coords, U_data, U_inf, x_position)

print(f"Maximum Velocity Deficit: {wake_params['deficit_max']:.3f} m/s")
print(f"Deficit Coefficient: {wake_params['deficit_max_coefficient']:.3f}")
print(f"Wake Width (50%): {wake_params['wake_width']:.4f} m")
```

> **📂 Source:** Wake analysis fundamentals  
> **คำอธิบาย (Explanation):** Gaussian profile เป็น approximation ที่ดีสำหรับ wake ใน far-field region interpolation ใช้หา wake width ที่แม่นยำ  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Velocity Deficit**: ความแตกต่างจาก freestream
> - **Wake Width**: ขนาดของ region ที่ได้รับอิทธิพล
> - **Centerline**: เส้นกลางของ wake (maximum deficit)
> - **Gaussian Approximation**: ใช้ได้ใน far wake

### 5.3 การพล็อต Wake Visualization

```python
# NOTE: Synthesized by AI - Verify parameters
def plot_wake_profile(y_coords, U_data, U_inf, wake_params, ax=None):
    """
    Plot wake profile with annotations

    Parameters:
    -----------
    y_coords : numpy.ndarray
        y coordinates [m]
    U_data : numpy.ndarray
        Velocity [m/s]
    U_inf : float
        Freestream velocity [m/s]
    wake_params : dict
        Wake parameters from analyze_wake_profile()
    ax : matplotlib.axes.Axes, optional
        Axes object
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    # Plot velocity profile
    ax.plot(U_data, y_coords, 'b-', linewidth=2, label='Velocity Profile')
    ax.fill_betweenx(y_coords, U_data, U_inf, alpha=0.2, color='red',
                     label='Velocity Deficit')

    # Plot U_inf
    ax.axvline(U_inf, color='r', linestyle='--', alpha=0.7,
               label=f'$U_\\infty$ = {U_inf} m/s')

    # Mark centerline
    ax.axhline(wake_params['centerline_y'], color='g', linestyle=':', alpha=0.5)
    ax.plot(wake_params['centerline_velocity'], wake_params['centerline_y'],
            'go', markersize=8, label='Wake Centerline')

    # Mark wake width
    if not np.isnan(wake_params['wake_width']):
        y1 = wake_params['centerline_y'] - wake_params['wake_width'] / 2
        y2 = wake_params['centerline_y'] + wake_params['wake_width'] / 2
        ax.plot([U_inf - wake_params['deficit_max']/2] * 2, [y1, y2],
                'r-', linewidth=3, label='Wake Width (50%)')

    # Labels and title
    ax.set_xlabel('$U_x$ [m/s]', fontsize=14)
    ax.set_ylabel('$y$ [m]', fontsize=14)
    ax.set_title(f'Wake Profile at x = {wake_params["x_position"]:.2f} m',
                 fontsize=16)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)

    # Add parameter text box
    textstr = f'$\\Delta U_{{max}}$ = {wake_params["deficit_max"]:.3f} m/s\n'
    textstr += f'$C_{{d,max}}$ = {wake_params["deficit_max_coefficient"]:.3f}\n'
    textstr += f'$w_{{0.5}}$ = {wake_params["wake_width"]:.3f} m'

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    return ax

# Example usage
fig, ax = plt.subplots(figsize=(10, 6))
plot_wake_profile(y_coords, U_data, U_inf, wake_params, ax=ax)
plt.tight_layout()
plt.savefig('wake_profile.pdf', dpi=300)
plt.show()
```

> **📂 Source:** Wake visualization techniques  
> **คำอธิบาย (Explanation):** การพล็อต velocity บน x-axis แสดงให้เห็น velocity deficit อย่างชัดเจน  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Profile Orientation**: Horizontal velocity vs vertical distance
> - **Deficit Visualization**: Fill region ระหว่าง profile กับ U∞
> - **Key Markers**: Centerline และ wake width
> - **Parameter Display**: Text box สรุปค่าสำคัญ

---

## 6. การวิเคราะห์สถิติข้อมูล CFD (Statistical Analysis)

### 6.1 การคำนวณค่าเฉลี่ยและการกระจาย

```python
# NOTE: Synthesized by AI - Verify parameters
import numpy as np
import pandas as pd

def analyze_field_statistics(field_data, field_name='U'):
    """
    Analyze statistics of CFD field

    Parameters:
    -----------
    field_data : numpy.ndarray
        Field data (shape: [n_cells, 3] for vector or [n_cells] for scalar)
    field_name : str
        Field name for reporting

    Returns:
    --------
    dict
        Field statistics
    """

    stats = {}
    stats['field_name'] = field_name

    if field_data.ndim == 2 and field_data.shape[1] == 3:
        # Vector field
        stats['type'] = 'vector'

        # Magnitude
        magnitude = np.linalg.norm(field_data, axis=1)
        stats['magnitude'] = {
            'mean': np.mean(magnitude),
            'std': np.std(magnitude),
            'min': np.min(magnitude),
            'max': np.max(magnitude),
            'median': np.median(magnitude)
        }

        # Components
        for i, comp in enumerate(['x', 'y', 'z']):
            stats[f'{comp}_component'] = {
                'mean': np.mean(field_data[:, i]),
                'std': np.std(field_data[:, i]),
                'min': np.min(field_data[:, i]),
                'max': np.max(field_data[:, i])
            }

        # Direction angles
        theta = np.arctan2(field_data[:, 1], field_data[:, 0]) * 180 / np.pi
        phi = np.arccos(field_data[:, 2] / magnitude) * 180 / np.pi

        stats['direction'] = {
            'theta_mean': np.mean(theta),
            'theta_std': np.std(theta),
            'phi_mean': np.mean(phi),
            'phi_std': np.std(phi)
        }

    else:
        # Scalar field
        stats['type'] = 'scalar'
        stats['value'] = {
            'mean': np.mean(field_data),
            'std': np.std(field_data),
            'min': np.min(field_data),
            'max': np.max(field_data),
            'median': np.median(field_data)
        }

    return stats

def print_field_statistics(stats):
    """Print field statistics beautifully"""
    print(f"\n{'='*60}")
    print(f"Field Statistics: {stats['field_name']}")
    print(f"Type: {stats['type'].upper()}")
    print(f"{'='*60}")

    if stats['type'] == 'vector':
        mag = stats['magnitude']
        print(f"\nMagnitude:")
        print(f"  Mean:   {mag['mean']:.6f}")
        print(f"  Std:    {mag['std']:.6f}")
        print(f"  Min:    {mag['min']:.6f}")
        print(f"  Max:    {mag['max']:.6f}")
        print(f"  Median: {mag['median']:.6f}")

        for comp in ['x', 'y', 'z']:
            c = stats[f'{comp}_component']
            print(f"\n{comp.upper()}-Component:")
            print(f"  Mean: {c['mean']:.6f}")
            print(f"  Std:  {c['std']:.6f}")
            print(f"  Min:  {c['min']:.6f}")
            print(f"  Max:  {c['max']:.6f}")
    else:
        val = stats['value']
        print(f"\nValue:")
        print(f"  Mean:   {val['mean']:.6f}")
        print(f"  Std:    {val['std']:.6f}")
        print(f"  Min:    {val['min']:.6f}")
        print(f"  Max:    {val['max']:.6f}")
        print(f"  Median: {val['median']:.6f}")
```

> **📂 Source:** Statistical analysis for CFD fields  
> **คำอธิบาย (Explanation):** ฟังก์ชันนี้จัดการทั้ง scalar และ vector fields โดยอัตโนมัติ คำนวณทั้ง magnitude และ components  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Vector vs Scalar**: จัดการทั้งสองประเภท
> - **Magnitude Analysis**: ขนาดของ vector
> - **Component Analysis**: แต่ละ directional component
> - **Direction Angles**: Spherical coordinates (θ, φ)

### 6.2 การวิเคราะห์ Histogram และ PDF

```python
# NOTE: Synthesized by AI - Verify parameters
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

def plot_field_distribution(field_data, field_name='U_mag', ax=None):
    """
    Plot field distribution (Histogram + PDF)

    Parameters:
    -----------
    field_data : numpy.ndarray
        Field data (1D array)
    field_name : str
        Field name for label
    ax : matplotlib.axes.Axes, optional
        Axes object
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    # Histogram
    n, bins, patches = ax.hist(field_data, bins=50, density=True,
                                alpha=0.6, label='Histogram',
                                edgecolor='black', linewidth=0.5)

    # Kernel Density Estimation (smooth PDF)
    kde = gaussian_kde(field_data)
    x_range = np.linspace(field_data.min(), field_data.max(), 200)
    pdf = kde(x_range)
    ax.plot(x_range, pdf, 'r-', linewidth=2, label='KDE PDF')

    # Statistics
    mean_val = np.mean(field_data)
    std_val = np.std(field_data)
    median_val = np.median(field_data)

    # Mark mean and median
    ax.axvline(mean_val, color='g', linestyle='--', linewidth=2,
               label=f'Mean = {mean_val:.3f}')
    ax.axvline(median_val, color='orange', linestyle='-.', linewidth=2,
               label=f'Median = {median_val:.3f}')

    # Labels
    ax.set_xlabel(field_name, fontsize=14)
    ax.set_ylabel('Probability Density', fontsize=14)
    ax.set_title(f'Distribution of {field_name}', fontsize=16)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add statistics text
    textstr = f'Mean:   {mean_val:.4f}\n'
    textstr += f'Std:    {std_val:.4f}\n'
    textstr += f'Median: {median_val:.4f}\n'
    textstr += f'Min:    {field_data.min():.4f}\n'
    textstr += f'Max:    {field_data.max():.4f}'

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', bbox=props)

    return ax
```

> **📂 Source:** Probability density visualization  
> **คำอธิบาย (Explanation):** KDE ให้ smooth PDF curve โดยไม่ต้องเลือก bin sizes อย่าง manual  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Histogram**: Discrete distribution
> - **Kernel Density Estimation**: Continuous PDF approximation
> - **Statistical Moments**: Mean, median, standard deviation
> - **Distribution Shape**: Skewness, kurtosis (visual)

---

## 7. การวิเคราะห์ Time Series (Temporal Analysis)

### 7.1 การพล็อต Monitor Variables ตามเวลา

```python
# NOTE: Synthesized by AI - Verify parameters
import pandas as pd
import matplotlib.pyplot as plt

def plot_time_series(time_data, variable_data, variable_name,
                     show_rolling_mean=False, window=10, ax=None):
    """
    Plot time series data

    Parameters:
    -----------
    time_data : numpy.ndarray
        Time data [s]
    variable_data : numpy.ndarray
        Variable data
    variable_name : str
        Variable name for label
    show_rolling_mean : bool
        Show rolling mean or not
    window : int
        Window size for rolling mean
    ax : matplotlib.axes.Axes, optional
        Axes object
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))

    # Plot raw data
    ax.plot(time_data, variable_data, 'b-', linewidth=0.5, alpha=0.7,
            label='Raw Data')

    # Plot rolling mean
    if show_rolling_mean:
        df = pd.DataFrame({'time': time_data, 'value': variable_data})
        rolling_mean = df['value'].rolling(window=window, center=True).mean()
        ax.plot(time_data, rolling_mean, 'r-', linewidth=2,
                label=f'Rolling Mean (window={window})')

    # Labels
    ax.set_xlabel('Time [s]', fontsize=14)
    ax.set_ylabel(f'{variable_name}', fontsize=14)
    ax.set_title(f'Time Series: {variable_name}', fontsize=16)
    ax.legend()
    ax.grid(True, alpha=0.3)

    return ax

def plot_convergence_history(residuals_data, ax=None):
    """
    Plot solver convergence history

    Parameters:
    -----------
    residuals_data : dict
        Dictionary of residuals, e.g., {'U': [...], 'p': [...]}
    ax : matplotlib.axes.Axes, optional
        Axes object
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    iterations = np.arange(1, len(residuals_data[list(residuals_data.keys())[0]]) + 1)

    for field_name, residuals in residuals_data.items():
        ax.semilogy(iterations, residuals, linewidth=2, label=field_name)

    ax.set_xlabel('Iteration', fontsize=14)
    ax.set_ylabel('Residual', fontsize=14)
    ax.set_title('Solver Convergence History', fontsize=16)
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')

    return ax
```

> **📂 Source:** Time series analysis for CFD  
> **คำอธิบาย (Explanation):** Rolling mean ช่วยลด noise ในข้อมูล temporal convergence history ใช้ log-scale เพื่อแสดง reduction หลาย orders  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Temporal Trends**: Monitor variables vs time
> - **Noise Reduction**: Rolling mean smooths fluctuations
> - **Convergence Monitoring**: Residuals drop over iterations
> - **Log Scale**: Visualize orders of magnitude

### 7.2 การวิเคราะห์ FFT (Frequency Domain)

สำหรับการวิเคราะห์ Unsteady Flow เช่น Vortex Shedding:

```python
# NOTE: Synthesized by AI - Verify parameters
from scipy.fft import fft, fftfreq

def analyze_fft(time_data, signal_data, sampling_rate=None):
    """
    Analyze FFT of signal

    Parameters:
    -----------
    time_data : numpy.ndarray
        Time data [s]
    signal_data : numpy.ndarray
        Signal (e.g., Lift coefficient vs time)
    sampling_rate : float, optional
        Sampling rate [Hz] (if None, calculated from time_data)

    Returns:
    --------
    dict
        FFT results:
        - frequencies: Frequency array [Hz]
        - amplitudes: Amplitude spectrum
        - dominant_freq: Dominant frequency [Hz]
        - dominant_amplitude: Amplitude at dominant frequency
    """

    N = len(signal_data)

    # Calculate sampling rate
    if sampling_rate is None:
        dt = np.mean(np.diff(time_data))
        sampling_rate = 1.0 / dt

    # FFT
    fft_values = fft(signal_data)
    amplitudes = 2.0 / N * np.abs(fft_values[0:N//2])
    frequencies = fftfreq(N, 1.0/sampling_rate)[0:N//2]

    # Find dominant frequency (skip DC component at index 0)
    dominant_idx = np.argmax(amplitudes[1:]) + 1
    dominant_freq = frequencies[dominant_idx]
    dominant_amplitude = amplitudes[dominant_idx]

    return {
        'frequencies': frequencies,
        'amplitudes': amplitudes,
        'dominant_freq': dominant_freq,
        'dominant_amplitude': dominant_amplitude
    }

def plot_fft_spectrum(frequencies, amplitudes, dominant_freq, ax=None):
    """
    Plot FFT spectrum

    Parameters:
    -----------
    frequencies : numpy.ndarray
        Frequency array [Hz]
    amplitudes : numpy.ndarray
        Amplitude spectrum
    dominant_freq : float
        Dominant frequency [Hz]
    ax : matplotlib.axes.Axes, optional
        Axes object
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    # Plot spectrum
    ax.plot(frequencies, amplitudes, 'b-', linewidth=1)

    # Highlight dominant frequency
    dominant_amp = amplitudes[np.argmin(np.abs(frequencies - dominant_freq))]
    ax.plot(dominant_freq, dominant_amp, 'ro', markersize=10,
            label=f'$f_{{dominant}}$ = {dominant_freq:.3f} Hz')
    ax.axvline(dominant_freq, color='r', linestyle='--', alpha=0.5)

    # Labels
    ax.set_xlabel('Frequency [Hz]', fontsize=14)
    ax.set_ylabel('Amplitude', fontsize=14)
    ax.set_title('FFT Spectrum', fontsize=16)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, frequencies.max())

    return ax
```

> **📂 Source:** Frequency domain analysis for CFD  
> **คำอธิบาย (Explanation):** FFT แปลง temporal signal เป็น frequency spectrum ใช้วิเคราะห์ periodic phenomena  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Fourier Transform**: Time domain → Frequency domain
> - **Sampling Rate**: กำหนด maximum frequency (Nyquist)
> - **Dominant Frequency**: Peak in spectrum
> - **Strouhal Number**: Characterize vortex shedding (St = fL/U)

---

## 8. การเปรียบเทียบกรณีศึกษา (Case Comparison)

### 8.1 การพล็อต Multi-Case Comparison

```python
# NOTE: Synthesized by AI - Verify parameters
def plot_multiple_cases(data_dict, x_key, y_key, ax=None,
                        xlabel=None, ylabel=None, title=None,
                        legend_location='best'):
    """
    Plot multiple case studies

    Parameters:
    -----------
    data_dict : dict
        Dictionary of cases, e.g.:
        {
            'Case1': {'x': [...], 'y': [...]},
            'Case2': {'x': [...], 'y': [...]},
            ...
        }
    x_key : str
        Key name for x-axis data
    y_key : str
        Key name for y-axis data
    ax : matplotlib.axes.Axes, optional
        Axes object
    xlabel : str, optional
        Label for x-axis
    ylabel : str, optional
        Label for y-axis
    title : str, optional
        Plot title
    legend_location : str
        Legend position

    Returns:
    --------
    matplotlib.axes.Axes
        Plotted axes object
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    # Define colors and markers
    colors = plt.cm.tab10(np.linspace(0, 1, len(data_dict)))
    markers = ['o', 's', '^', 'd', 'v', '<', '>', 'p', '*', 'h']

    # Plot each case
    for idx, (case_name, case_data) in enumerate(data_dict.items()):
        x_data = case_data[x_key]
        y_data = case_data[y_key]

        ax.plot(x_data, y_data,
                marker=markers[idx % len(markers)],
                color=colors[idx],
                linewidth=2,
                markersize=6,
                label=case_name)

    # Labels
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=14)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=14)
    if title:
        ax.set_title(title, fontsize=16)

    ax.legend(loc=legend_location)
    ax.grid(True, alpha=0.3)

    return ax
```

> **📂 Source:** Multi-case visualization standards  
> **คำอธิบาย (Explanation):** ใช้ color cycle และ marker variations เพื่อแยกแยะกรณีศึกษา  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Data Organization**: Dictionary ของ cases
> - **Visual Distinction**: Colors และ markers
> - **Legend Management**: Clear identification
> - **Comparison Plots**: Side-by-side analysis

### 8.2 การพล็อต Convergence Study

```python
# NOTE: Synthesized by AI - Verify parameters
def plot_mesh_convergence(mesh_sizes, error_values,
                          quantity_name='Error', ax=None):
    """
    Plot mesh convergence study

    Parameters:
    -----------
    mesh_sizes : list or numpy.ndarray
        Mesh sizes (e.g., number of cells)
    error_values : list or numpy.ndarray
        Corresponding error values
    quantity_name : str
        Quantity name for label
    ax : matplotlib.axes.Axes, optional
        Axes object
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    # Plot data points
    ax.loglog(mesh_sizes, error_values, 'bo-', linewidth=2, markersize=8,
              label='Simulation Data')

    # Fit power law: error = C * N^(-p)
    from scipy.optimize import curve_fit

    def power_law(N, C, p):
        return C * N**(-p)

    try:
        popt, _ = curve_fit(power_law, mesh_sizes, error_values)
        N_fit = np.logspace(np.log10(mesh_sizes.min()),
                           np.log10(mesh_sizes.max()), 100)
        error_fit = power_law(N_fit, *popt)

        ax.loglog(N_fit, error_fit, 'r--', linewidth=2,
                  label=f'Fit: Error $\\propto N^{{{-popt[1]:.2f}}}$')

        # Display order of convergence
        textstr = f'Order of Convergence: {popt[1]:.3f}'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', bbox=props)
    except:
        pass

    # Labels
    ax.set_xlabel('Mesh Size (Number of Cells)', fontsize=14)
    ax.set_ylabel(quantity_name, fontsize=14)
    ax.set_title('Mesh Convergence Study', fontsize=16)
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')

    return ax
```

> **📂 Source:** Mesh convergence analysis  
> **คำอธิบาย (Explanation):** Power law fit ให้ order of convergence ($p$) ซึ่งบอกว่า mesh refinement ลด error อย่างไร  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Grid Convergence**: Error ลดลงเมื่อ mesh ละเอียดขึ้น
> - **Order of Convergence**: Exponent ใน power law
> - **Log-Log Plot**: Linearize power law relationship
> - **Richardson Extrapolation**: ประมาณค่าที่ mesh-independent

---

## 9. มาตรฐานการรายงานระดับมืออาชีพ (Professional Standards)

### 9.1 ข้อกำหนดสำหรับการตีพิมพ์ (Publication Requirements)

เพื่อให้กราฟจาก Python มีความน่าเชื่อถือและเป็นมืออาชีพ ควรปฏิบัติตามหลักการดังนี้:

#### 9.1.1 Typography

- **Serif Fonts** (เช่น Times New Roman) สำหรับวารสารวิทยาศาสตร์
- **Sans-serif Fonts** (เช่น Helvetica, Arial) สำหรับรายงานทางเทคนิค
- ขนาดฟอนต์: Title (16-18 pt), Axis Labels (12-14 pt), Tick Labels (10-12 pt)

#### 9.1.2 Legend & Label

- ต้องระบุชื่อตัวแปรและหน่วย (Units) อย่างชัดเจนเสมอ
- ตัวอย่าง: $U$ [m/s] หรือ $p - p_{\infty}$ [Pa]
- Legend ควรอยู่ในตำแหน่งที่ไม่บดบังข้อมูล

#### 9.1.3 Dimensionless Scaling

เมื่อเป็นไปได้ ควรพล็อตข้อมูลในรูปของค่าไร้มิติ:
- $y/L$ หรือ $y/D$ สำหรับระยะทาง
- $U/U_{\infty}$ สำหรับความเร็ว
- $C_p = (p - p_{\infty}) / (0.5 \rho U_{\infty}^2)$ สำหรับความดัน

### 9.2 ตัวอย่างการตั้งค่า Matplotlib แบบ Complete

```python
# NOTE: Synthesized by AI - Verify parameters
# File: plot_config.py

import matplotlib.pyplot as plt
import numpy as np

# Professional settings
def setup_publication_style():
    """
    Setup Matplotlib for publication
    """

    plt.rcParams.update({
        # Font settings
        'font.family': 'serif',
        'font.serif': ['Times New Roman'],
        'font.size': 12,
        'axes.labelsize': 14,
        'axes.titlesize': 16,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 11,

        # Figure settings
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.format': 'pdf',
        'savefig.bbox': 'tight',

        # Line settings
        'lines.linewidth': 1.5,
        'lines.markersize': 8,

        # Axes settings
        'axes.linewidth': 1.0,
        'axes.unicode_minus': False,  # Use hyphen instead of minus sign

        # Grid settings
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linewidth': 0.5,
        'grid.linestyle': '--',

        # Legend settings
        'legend.frameon': True,
        'legend.framealpha': 0.8,
        'legend.edgecolor': 'gray',

        # LaTeX settings (if LaTeX is installed)
        'text.usetex': False,  # Set True if LaTeX is available
    })

def save_figure(fig, filename, formats=['pdf', 'png'], dpi=300):
    """
    Save figure in multiple formats

    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        Figure object
    filename : str
        Filename (without extension)
    formats : list
        List of formats to save
    dpi : int
        DPI for raster formats
    """

    for fmt in formats:
        if fmt == 'pdf':
            fig.savefig(f'{filename}.pdf', format='pdf', bbox_inches='tight')
        elif fmt == 'png':
            fig.savefig(f'{filename}.png', format='png', dpi=dpi,
                       bbox_inches='tight')
        elif fmt == 'svg':
            fig.savefig(f'{filename}.svg', format='svg', bbox_inches='tight')

    print(f"Figure saved: {filename} ({', '.join(formats)})")

# Example usage
if __name__ == "__main__":
    setup_publication_style()

    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x)

    ax.plot(x, y, 'b-', linewidth=2, label='$\\sin(x)$')
    ax.set_xlabel('$x$ [rad]')
    ax.set_ylabel('$y$')
    ax.set_title('Example Plot')
    ax.legend()
    ax.grid(True)

    save_figure(fig, 'example_plot', formats=['pdf', 'png'])
```

> **📂 Source:** Publication-quality plotting standards  
> **คำอธิบาย (Explanation):** การตั้งค่า rcParams ทั่วทั้ง script ทำให้ทุกกราฟมี style สม่ำเสมอ PDF format รักษา vector quality  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Journal Requirements**: Typography และ DPI standards
> - **Vector Graphics**: PDF/SVG สำหรับ scalability
> - **Style Consistency**: rcParams สำหรับ uniform appearance
> - **Multi-format Export**: PDF สำหรับ printing, PNG สำหรับ presentations

### 9.3 Color Palettes สำหรับ CFD Visualization

> [!WARNING) ข้อควรระวังในการเลือกสี
> - **ใช้ Perceptually Uniform Colormaps** เช่น `viridis`, `plasma`, `cividis`
> - **หลีกเลี่ยง Rainbow Colormap** (jet/rainbow) สำหรับข้อมูล sequential
> - **ใช้ Diverging Colormaps** เช่น `coolwarm`, `RdBu` สำหรับข้อมูลที่มีจุดศูนย์กลางชัดเจน

```python
# NOTE: Synthesized by AI - Verify parameters
def get_cfd_colormap(cmap_type='sequential'):
    """
    Return appropriate colormap for CFD

    Parameters:
    -----------
    cmap_type : str
        Colormap type: 'sequential', 'diverging', 'qualitative'

    Returns:
    --------
    matplotlib.colors.Colormap
        Colormap object
    """

    if cmap_type == 'sequential':
        return plt.cm.viridis
    elif cmap_type == 'diverging':
        return plt.cm.coolwarm
    elif cmap_type == 'qualitative':
        return plt.cm.tab10
    else:
        return plt.cm.viridis
```

> **📂 Source:** Color theory for scientific visualization  
> **คำอธิบาย (Explanation):** Perceptually uniform colormaps มีการเปลี่ยนสีที่สม่ำเสมอตาม perceived brightness ทำให้ตีความได้ถูกต้อง  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Perceptual Uniformity**: Equal steps in data = equal steps in perception
> - **Color Blindness**: Viridis/cividis อ่านได้กับ color vision deficiencies
> - **Sequential Data**: Single-direction changes (e.g., temperature)
> - **Diverging Data**: Deviation from midpoint (e.g., pressure difference)

---

## 10. การสร้างรายงานอัตโนมัติ (Automated Reporting)

### 10.1 การสร้าง Multi-Panel Figures

```python
# NOTE: Synthesized by AI - Verify parameters
def create_multipanel_figure(fig_size=(12, 10), nrows=2, ncols=2):
    """
    Create multi-panel figure for reports

    Returns:
    --------
    tuple
        (fig, axes) where axes is array of Axes objects
    """

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols,
                            figsize=fig_size,
                            constrained_layout=True)

    # Flatten axes array if needed
    if nrows == 1 or ncols == 1:
        axes = np.array(axes).flatten()
    else:
        axes = axes.flatten()

    # Add figure label (a, b, c, ...)
    for idx, ax in enumerate(axes):
        label = chr(97 + idx)  # a, b, c, ...
        ax.text(0.02, 0.98, f'({label})', transform=ax.transAxes,
               fontsize=14, fontweight='bold', va='top')

    return fig, axes

# Example usage
fig, axes = create_multipanel_figure((14, 10), 2, 2)

# Panel (a): Velocity Profile
plot_velocity_profile(y, U, U_inf, bl_params, ax=axes[0])

# Panel (b): Wake Profile
plot_wake_profile(y_coords, U_data, U_inf, wake_params, ax=axes[1])

# Panel (c): Field Statistics
plot_field_distribution(U_mag, '$|\\mathbf{U}|$ [m/s]', ax=axes[2])

# Panel (d): FFT Spectrum
plot_fft_spectrum(frequencies, amplitudes, dominant_freq, ax=axes[3])

# Add overall title
fig.suptitle('CFD Analysis Summary', fontsize=18, fontweight='bold')

# Save
save_figure(fig, 'cfd_analysis_summary', formats=['pdf', 'png'])
```

> **📂 Source:** Multi-panel figure composition  
> **คำอธิบาย (Explanation):** `constrained_layout` จัดการ spacing ระหว่าง panels อัตโนมัติ ป้ายกำกับ (a), (b), ... ช่วยอ้างอิงใน text  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Subplot Grid**: nrows x ncols arrangement
> - **Constrained Layout**: Automatic spacing optimization
> - **Panel Labels**: (a), (b), (c) references
> - **Unified Style**: Consistent across all panels

### 10.2 การสร้าง PDF Report ด้วย Python

```python
# NOTE: Synthesized by AI - Verify parameters
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

def create_pdf_report(output_filename, case_name, metadata_dict):
    """
    Create multi-page PDF report

    Parameters:
    -----------
    output_filename : str
        PDF output filename
    case_name : str
        Case study name
    metadata_dict : dict
        Metadata such as solver, mesh, etc.
    """

    with PdfPages(output_filename) as pdf:
        # Page 1: Summary
        fig = plt.figure(figsize=(11, 8.5))
        fig.text(0.5, 0.9, f'CFD Analysis Report: {case_name}',
                ha='center', fontsize=20, fontweight='bold')

        # Metadata
        y_pos = 0.8
        for key, value in metadata_dict.items():
            fig.text(0.1, y_pos, f'{key}: {value}', fontsize=12)
            y_pos -= 0.05

        fig.text(0.5, 0.05,
                f'Generated: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}',
                ha='center', fontsize=10, style='italic')

        # Remove axes
        plt.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

        # Page 2-N: Plots (add your plots here)
        # ...

        # Add metadata to PDF
        d = pdf.infodict()
        d['Title'] = f'CFD Report: {case_name}'
        d['Author'] = 'OpenFOAM Python Automation'
        d['Subject'] = 'Computational Fluid Dynamics Analysis'
        d['Keywords'] = 'OpenFOAM, CFD, Python, Visualization'
        d['CreationDate'] = pd.Timestamp.now()

    print(f"PDF Report created: {output_filename}")

# Example usage
metadata = {
    'Solver': 'simpleFoam',
    'Turbulence Model': 'k-omega SST',
    'Mesh Size': '2.5M cells',
    'Reynolds Number': '1e5',
    'Boundary Conditions': 'U_inf = 10 m/s'
}

create_pdf_report('cfd_report.pdf', 'FlowAroundCylinder', metadata)
```

> **📂 Source:** PDF generation with Matplotlib  
> **คำอธิบาย (Explanation):** `PdfPages` context manager สร้าง multi-page PDF พร้อม metadata embeddings  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Multi-page Documents**: หลาย figures ใน PDF เดียว
> - **PDF Metadata**: Title, author, keywords embedded
> - **Automated Workflows**: สร้าง reports จาก scripts
> - **Version Control**: Timestamps ใน reports

---

## 11. ตัวอย่างการวิเคราะห์กรณีศึกษา (Example Case Studies)

### 11.1 การวิเคราะห์ Flow Around Cylinder

> **[MISSING DATA]**: Insert specific simulation results/graphs for Flow around Cylinder case.

**สิ่งที่ต้องวิเคราะห์:**
- **Vortex Shedding Frequency**: ใช้ Lift Coefficient vs Time
- **Drag Coefficient**: ใช้ Pressure และ Wall Shear Stress
- **Strouhal Number**: $St = \frac{fL}{U_{\infty}}$

**เทมเพลตการวิเคราะห์:**

```python
# NOTE: Synthesized by AI - Verify parameters
def analyze_cylinder_flow(forces_data, U_inf, diameter, rho):
    """
    Analyze flow around cylinder

    Parameters:
    -----------
    forces_data : pandas.DataFrame
        Forces vs time data
    U_inf : float
        Freestream velocity [m/s]
    diameter : float
        Cylinder diameter [m]
    rho : float
        Density [kg/m³]

    Returns:
    --------
    dict
        Analysis results
    """

    results = {}

    # Calculate Cd and Cl
    A_ref = diameter * 1.0  # Unit depth
    Cd = 2 * forces_data['Fx_total'] / (rho * U_inf**2 * A_ref)
    Cl = 2 * forces_data['Fy_total'] / (rho * U_inf**2 * A_ref)

    # Mean values
    results['Cd_mean'] = np.mean(Cd[len(Cd)//2:])  # Second half only
    results['Cl_mean'] = np.mean(Cl[len(Cl)//2:])

    # FFT analysis for vortex shedding
    time = forces_data['Time'].values
    cl_signal = Cl.values

    fft_results = analyze_fft(time, cl_signal)

    results['shedding_frequency'] = fft_results['dominant_freq']

    # Strouhal number
    results['Strouhal'] = (results['shedding_frequency'] * diameter) / U_inf

    return results
```

> **📂 Source:** Flow around cylinder analysis  
> **คำอธิบาย (Explanation):** วิเคราะห์ Cd, Cl และ Strouhal number เพื่อ validate กับ literature values (St ≈ 0.2 สำหรับ cylinder)  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Drag Coefficient**: Resistance force in flow direction
> - **Lift Coefficient**: Oscillating force (vortex shedding)
> - **Strouhal Number**: Dimensionless shedding frequency
> - **Von Kármán Vortex Street**: Alternating vortex pattern

### 11.2 การวิเคราะห์ Turbulent Channel Flow

> **[MISSING DATA]**: Insert specific simulation results/graphs for Turbulent Channel Flow case.

**สิ่งที่ต้องวิเคราะห์:**
- **Velocity Profile**: $u^+$ vs $y^+$ (Law of the Wall)
- **Turbulence Statistics**: $k$, $\omega$, $\nu_t$
- **Reynolds Stress**: $-\rho \overline{u'v'}$

---

## 12. แนวทางการแก้ปัญหา (Troubleshooting)

> [!WARNING) ปัญหาที่พบบ่อย
>
> **ปัญหา**: ไฟล์ CSV ไม่สามารถอ่านได้
> - **สาเหตุ**: Comment lines หรือ header format ไม่ถูกต้อง
> - **วิธีแก้**: ใช้ `comment='#'` หรือตรวจสอบ `skiprows`
>
> **ปัญหา**: Memory error เมื่อโหลดข้อมูลขนาดใหญ่
> - **สาเหตุ**: ข้อมูล mesh ละเอียดเกินไป
> - **วิธีแก้**: ใช้ `chunksize` ใน pandas หรือ sampling ข้อมูล
>
> **ปัญหา**: กราฟมีความละเอียดต่ำเมื่อส่งออก
> - **สาเหตุ**: การตั้งค่า DPI ไม่เพียงพอ
> - **วิธีแก้**: ใช้ `dpi=300` หรือสูงกว่า และบันทึกเป็น PDF/SVG

> [!TIP) เคล็ดลับการใช้ Matplotlib
> - ใช้ `constrained_layout=True` เพื่อจัดการ spacing อัตโนมัติ
> - ใช้ `bbox_inches='tight'` เมื่อบันทึกเพื่อหลีกเลี่ยง text ถูกตัด
> - ใช้ `gridspec` สำหรับ layout ที่ซับซ้อน

---

## 13. บทสรุป (Summary)

การใช้ Python ในการพล็อตผลลัพธ์ช่วยยกระดับจากการแค่ "ดูผล" (Qualitative) ไปสู่การ "วิเคราะห์ผล" (Quantitative) ที่แม่นยำและสามารถนำไปอ้างอิงทางวิชาการหรือวิศวกรรมขั้นสูงได้

**ข้อดีหลัก:**
- **Automation**: สร้างกราฟจากหลายกรณีศึกษาได้อัตโนมัติ
- **Reproducibility**: Scripts สามารถใช้ซ้ำและแบ่งปันได้
- **Publication Quality**: ควบคุมคุณภาพรูปภาพได้อย่างละเอียด
- **Integration**: เชื่อมต่อกับ NumPy, SciPy, Pandas สำหรับการวิเคราะห์ขั้นสูง

**เอกสารที่เกี่ยวข้อง:**
- [[00_Overview]] - เวิร์กโฟลว์การสร้างภาพและการเลือกเครื่องมือ
- [[01_ParaView_Visualization]] - การสร้างภาพ 3 มิติและการใช้ ParaView
- [[../03_POST_PROCESSING]] - การใช้ OpenFOAM Utilities เพื่อสกัดข้อมูลสำหรับ Python

---

## 14. อ้างอิงและแหล่งเรียนรู้เพิ่มเติม

**เอกสาร Python Visualization:**
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
- [Seaborn Statistical Graphics](https://seaborn.pydata.org/)
- [Plotly Python Library](https://plotly.com/python/)

**หนังสือแนะนำ:**
- "Python for Data Analysis" by Wes McKinney
- "Scientific Visualization: Python + Matplotlib" โดยคนไทย

**แหล่งเรียนรู้ออนไลน์:**
- [Matplotlib Tutorials](https://matplotlib.org/stable/tutorials/index.html)
- [Real Python: Python Plotting Tutorial](https://realpython.com/python-matplotlib-guide/)

**Tools และ Libraries:**
- [NumPy](https://numpy.org/) - Numerical computing
- [SciPy](https://www.scipy.org/) - Scientific computing
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [PyVista](https://pyvista.org/) - 3D visualization in Python

---

## Appendix A: Code Templates

### A.1 Complete Analysis Script Template

```python
# NOTE: Synthesized by AI - Verify parameters
#!/usr/bin/env python3
"""
OpenFOAM Python Analysis Script
Case: Flow Around Cylinder
Date: 2024-XX-XX
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import simpson
from scipy.fft import fft, fftfreq

# Configuration
CASE_DIR = "postProcessing"
U_INF = 10.0  # m/s
RHO = 1.225   # kg/m³
DIAMETER = 0.1  # m

def main():
    """Main analysis function"""

    print("="*60)
    print("OpenFOAM Python Analysis Script")
    print("="*60)

    # Setup plotting style
    setup_publication_style()

    # 1. Load data
    print("\n[1] Loading data...")
    forces_data = read_forces_data(f'{CASE_DIR}/forces/0/forces.dat')

    # 2. Analyze forces
    print("\n[2] Analyzing forces...")
    results = analyze_cylinder_flow(forces_data, U_INF, DIAMETER, RHO)

    # 3. Plot results
    print("\n[3] Generating plots...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Add your plots here...

    # 4. Save report
    print("\n[4] Generating report...")
    save_figure(fig, 'cylinder_flow_analysis')

    # 5. Print summary
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    print(f"Drag Coefficient (Cd): {results['Cd_mean']:.4f}")
    print(f"Lift Coefficient (Cl): {results['Cl_mean']:.4f}")
    print(f"Shedding Frequency: {results['shedding_frequency']:.3f} Hz")
    print(f"Strouhal Number: {results['Strouhal']:.4f}")
    print("="*60)

if __name__ == "__main__":
    main()
```

> **📂 Source:** OpenFOAM Python automation workflow  
> **คำอธิบาย (Explanation):** Template นี้ให้โครงสร้างพื้นฐานสำหรับ CFD analysis scripts สามารถดัดแปลงให้เหมาะกับ cases ต่างๆ  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Script Organization**: Clear sections for load/analyze/plot/report
> - **Configuration**: Constants ที่จุดเดียว
> - **Progress Indicators**: Print statements แสดง workflow
> - **Error Handling**: Try-except blocks (สามารถเพิ่มได้)

### A.2 Jupyter Notebook Template

```python
# NOTE: Synthesized by AI - Verify parameters
# Jupyter Notebook for CFD Analysis

# Cell 1: Imports and Setup
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set plot style
rcParams['figure.dpi'] = 100
rcParams['savefig.dpi'] = 300
%matplotlib inline

# Cell 2: Load Data
forces = pd.read_csv('postProcessing/forces/0/forces.dat',
                     sep='\t', comment='#',
                     names=['Time', 'Fx_p', 'Fy_p', 'Fz_p',
                            'Fx_v', 'Fy_v', 'Fz_v',
                            'Fx_t', 'Fy_t', 'Fz_t',
                            'Mx', 'My', 'Mz'])

# Display first rows
forces.head()

# Cell 3: Analysis & Visualization
# Add your analysis code here...
```

> **📂 Source:** Jupyter Notebook for CFD  
> **คำอธิบาย (Explanation):** Jupyter notebooks เหมาะสำหรับ exploratory analysis และ documentation  
> **แนวคิดสำคัญ (Key Concepts):**
> - **Cell-based Execution**: Run code chunks independently
> - **Inline Plotting**: ` %matplotlib inline` แสดงกราฟใน notebook
> - **Interactive Exploration**: Rapid iteration
> - **Documentation**: Markdown cells สำหรับ explanations
> - **Export to PDF**: nbconvert สร้าง reports จาก notebooks

---

**END OF DOCUMENT**