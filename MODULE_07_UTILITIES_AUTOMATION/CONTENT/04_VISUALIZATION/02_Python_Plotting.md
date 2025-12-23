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
    A[OpenFOAM Results] --> B[postProcessing Data<br/>ASCII/CSV]
    B --> C[Python Data Loading<br/>Pandas/NumPy]
    C --> D[Data Analysis<br/>Stats/Integration]
    D --> E[Plot Generation<br/>Matplotlib]
    E --> F[Professional Reports<br/>PDF/LaTeX]

    style A fill:#e3f2fd
    style B fill:#bbdefb
    style C fill:#90caf9
    style D fill:#64b5f6
    style E fill:#42a5f5
    style F fill:#2196f3
```

![[plotting_workflow_visual.png]]
> **รูปที่ 1.1:** วงจรการทำงานของการพล็อตและวิเคราะห์ข้อมูล: จากการสกัดข้อมูลดิบไปจนถึงการจัดทำรูปเล่มรายงานทางเทคนิค

---

## 2. การติดตั้งและการเตรียมความพร้อม (Setup and Preparation)

### 2.1 การติดตั้ง Python Environment

สำหรับการวิเคราะห์ข้อมูล CFD แนะนำให้ใช้ Anaconda หรือ Miniconda:

```bash
# NOTE: Synthesized by AI - Verify parameters
# สร้าง Environment สำหรับ CFD Visualization
conda create -n cfd-vis python=3.11

# เปิดใช้งาน Environment
conda activate cfd-vis

# ติดตั้ง Libraries หลัก
conda install -c conda-forge matplotlib numpy pandas scipy

# ติดตั้น Libraries เพิ่มเติมสำหรับ Visualization
pip install seaborn plotly pyvista kaleido
```

### 2.2 การติดตั้ง PyFoam

PyFoam เป็น Python library สำหรับทำงานร่วมกับ OpenFOAM:

```bash
# NOTE: Synthesized by AI - Verify parameters
pip install PyFoam
# หรือใช้ conda
conda install -c conda-forge pyfoam
```

### 2.3 การตั้งค่า Matplotlib สำหรับการตีพิมพ์

ไฟล์ `matplotlibrc` หรือการตั้งค่าใน script:

```python
# NOTE: Synthesized by AI - Verify parameters
import matplotlib.pyplot as plt
import numpy as np

# การตั้งค่าระดับมืออาชีพสำหรับวารสารวิชาการ
plt.rcParams.update({
    # ฟอนต์และขนาดตัวอักษร
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 12,
    "axes.labelsize": 14,
    "axes.titlesize": 16,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,

    # คุณภาพของภาพ
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.format": "pdf",
    "savefig.bbox": "tight",

    # เส้นและสี
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

### 3.2 การอ่านข้อมูล CSV ด้วย Pandas

```python
# NOTE: Synthesized by AI - Verify parameters
import pandas as pd
import numpy as np

def read_openfoam_csv(filepath):
    """
    อ่านไฟล์ CSV จาก OpenFOAM sample utility

    Parameters:
    -----------
    filepath : str
        พาธไปยังไฟล์ CSV

    Returns:
    --------
    pandas.DataFrame
        ข้อมูลที่อ่านได้
    """
    # อ่านไฟล์ (ข้าม comment lines ที่ขึ้นต้นด้วย #)
    df = pd.read_csv(filepath, comment='#', skipinitialspace=True)

    return df

# ตัวอย่างการใช้งาน
velocity_data = read_openfoam_csv('postProcessing/surfaces/0.5/centreLine_U.csv')
print(velocity_data.head())
```

### 3.3 การอ่านข้อมูลจาก probes

```python
# NOTE: Synthesized by AI - Verify parameters
def read_probes_data(filepath):
    """
    อ่านข้อมูลจาก probes utility

    Parameters:
    -----------
    filepath : str
        พาธไปยังไฟล์ probes

    Returns:
    --------
    dict
        Dictionary ของ arrays สำหรับแต่ละ probe
    """
    data = {}
    current_probe = []
    probe_count = 0

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()

            # เริ่ม probe ใหม่
            if line.startswith('# Probe'):
                if current_probe:
                    data[f'probe_{probe_count}'] = np.array(current_probe)
                    current_probe = []
                    probe_count += 1

            # อ่านข้อมูล (ข้าม comment และ empty lines)
            elif line and not line.startswith('#'):
                values = [float(x) for x in line.split()]
                current_probe.append(values)

        # Probe สุดท้าย
        if current_probe:
            data[f'probe_{probe_count}'] = np.array(current_probe)

    return data

# ตัวอย่างการใช้งาน
probes_data = read_probes_data('postProcessing/probes/0.5/U')
```

### 3.4 การอ่านข้อมูล Forces

```python
# NOTE: Synthesized by AI - Verify parameters
def read_forces_data(filepath):
    """
    อ่านข้อมูล forces จาก forces utility

    Parameters:
    -----------
    filepath : str
        พาธไปยังไฟล์ forces.dat

    Returns:
    --------
    pandas.DataFrame
        ข้อมูล forces พร้อม column names
    """
    # อ่านไฟล์ (skip header ที่มี #)
    df = pd.read_csv(filepath,
                     sep='\t',
                     comment='#',
                     names=['Time',
                            'Fx_p', 'Fy_p', 'Fz_p',
                            'Fx_viscous', 'Fy_viscous', 'Fz_viscous',
                            'Fx_total', 'Fy_total', 'Fz_total',
                            'Mx', 'My', 'Mz'])

    return df

# ตัวอย่างการใช้งาน
forces_data = read_forces_data('postProcessing/forces/0/forces.dat')

# คำนวณ Drag และ Lift Coefficients
rho = 1.225      # kg/m³
U_inf = 10.0     # m/s
A_ref = 1.0      # m² (reference area)

# Drag coefficient (assuming drag in x-direction)
Cd = 2 * forces_data['Fx_total'] / (rho * U_inf**2 * A_ref)

# Lift coefficient (assuming lift in y-direction)
Cl = 2 * forces_data['Fy_total'] / (rho * U_inf**2 * A_ref)
```

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
    คำนวณพารามิเตอร์ Boundary Layer

    Parameters:
    -----------
    y : numpy.ndarray
        ตำแหน่งตามแนวปกติจากผนัง [m]
    U : numpy.ndarray
        ความเร็ว x-component ที่แต่ละตำแหน่ง y [m/s]
    U_inf : float
        ความเร็วกระแสอิสระ [m/s]

    Returns:
    --------
    dict
        Dictionary ของ boundary layer parameters:
        - delta_star: Displacement thickness
        - theta: Momentum thickness
        - H: Shape factor
        - delta_99: Boundary layer thickness (99% criterion)
    """

    # Normalize velocity
    U_norm = U / U_inf

    # คำนวณ Displacement thickness (Simpson's rule)
    delta_star = simpson(1 - U_norm, y)

    # คำนวณ Momentum thickness
    theta = simpson(U_norm * (1 - U_norm), y)

    # คำนวณ Shape factor
    H = delta_star / theta

    # คำนวณ Boundary layer thickness (99% criterion)
    delta_99 = np.interp(0.99 * U_inf, U, y)

    return {
        'delta_star': delta_star,
        'theta': theta,
        'H': H,
        'delta_99': delta_99
    }

# ตัวอย่างการใช้งาน
y = np.array([0.0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1])  # m
U = np.array([0.0, 0.5, 1.2, 3.5, 6.0, 8.5, 9.8, 10.0])         # m/s
U_inf = 10.0  # m/s

bl_params = calculate_boundary_layer_params(y, U, U_inf)

print(f"Displacement Thickness (δ*): {bl_params['delta_star']:.6f} m")
print(f"Momentum Thickness (θ):     {bl_params['theta']:.6f} m")
print(f"Shape Factor (H):           {bl_params['H']:.3f}")
print(f"Boundary Layer Thickness (δ99): {bl_params['delta_99']:.4f} m")
```

### 4.4 การพล็อต Velocity Profile

```python
# NOTE: Synthesized by AI - Verify parameters
import matplotlib.pyplot as plt

def plot_velocity_profile(y, U, U_inf, bl_params, ax=None):
    """
    พล็อต Velocity profile พร้อม boundary layer parameters

    Parameters:
    -----------
    y : numpy.ndarray
        ตำแหน่งตามแนวปกติจากผนัง [m]
    U : numpy.ndarray
        ความเร็ว x-component [m/s]
    U_inf : float
        ความเร็วกระแสอิสระ [m/s]
    bl_params : dict
        Boundary layer parameters จาก calculate_boundary_layer_params()
    ax : matplotlib.axes.Axes, optional
        Axes object สำหรับ plotting
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

# ตัวอย่างการใช้งาน
fig, ax = plt.subplots(figsize=(10, 6))
plot_velocity_profile(y, U, U_inf, bl_params, ax=ax)
plt.tight_layout()
plt.savefig('boundary_layer_profile.pdf', dpi=300)
plt.show()
```

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
    พล็อต Law of the Wall

    Parameters:
    -----------
    y : numpy.ndarray
        ตำแหน่งจากผนัง [m]
    U : numpy.ndarray
        ความเร็ว [m/s]
    nu : float
        Kinematic viscosity [m²/s]
    rho : float
        ความหนาแน่น [kg/m³]
    tau_w : float
        Wall shear stress [Pa]
    ax : matplotlib.axes.Axes, optional
        Axes object
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))

    # คำนวณ friction velocity
    u_tau = np.sqrt(tau_w / rho)

    # คำนวณ non-dimensional parameters
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
    วิเคราะห์ Wake profile ที่ตำแหน่ง x ที่กำหนด

    Parameters:
    -----------
    y_coords : numpy.ndarray
        พิกัด y ตามแนวตั้ง [m]
    U_data : numpy.ndarray
        ความเร็ว x-component ที่ตำแหน่ง x ที่กำหนด [m/s]
    U_inf : float
        ความเร็วกระแสอิสระ [m/s]
    x_position : float
        ตำแหน่ง x ที่วิเคราะห์ [m]

    Returns:
    --------
    dict
        Wake parameters:
        - deficit_max: Maximum velocity deficit
        - deficit_profile: Velocity deficit profile
        - wake_width: Wake width (50% criterion)
        - centerline_velocity: Velocity at wake centerline
    """

    # คำนวณ velocity deficit
    deficit = U_inf - U_data
    deficit_max = np.max(deficit)

    # หาตำแหน่ง centerline (maximum deficit)
    centerline_idx = np.argmax(deficit)
    centerline_velocity = U_data[centerline_idx]
    centerline_y = y_coords[centerline_idx]

    # คำนวณ wake width (50% criterion)
    half_deficit = deficit_max / 2.0

    # หาจุดที่ deficit = 0.5 * deficit_max
    from scipy.interpolate import interp1d

    # Interpolate เพื่อหาตำแหน่งที่แม่นยำ
    f = interp1d(y_coords, deficit - half_deficit, kind='linear')

    # หาจุดตัด (root finding)
    try:
        # ด้านซ้ายของ centerline
        y_left = y_coords[:centerline_idx]
        deficit_left = deficit[:centerline_idx] - half_deficit
        if np.any(deficit_left > 0) and np.any(deficit_left < 0):
            y1 = np.interp(0, deficit_left[::-1], y_left[::-1])
        else:
            y1 = y_coords[0]

        # ด้านขวาของ centerline
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

# ตัวอย่างการใช้งาน
y_coords = np.linspace(-0.5, 0.5, 100)
U_data = 10.0 - 3.0 * np.exp(-(y_coords / 0.15)**2)  # Gaussian wake profile
U_inf = 10.0
x_position = 2.0

wake_params = analyze_wake_profile(y_coords, U_data, U_inf, x_position)

print(f"Maximum Velocity Deficit: {wake_params['deficit_max']:.3f} m/s")
print(f"Deficit Coefficient: {wake_params['deficit_max_coefficient']:.3f}")
print(f"Wake Width (50%): {wake_params['wake_width']:.4f} m")
```

### 5.3 การพล็อต Wake Visualization

```python
# NOTE: Synthesized by AI - Verify parameters
def plot_wake_profile(y_coords, U_data, U_inf, wake_params, ax=None):
    """
    พล็อต Wake profile พร้อม annotations

    Parameters:
    -----------
    y_coords : numpy.ndarray
        พิกัด y [m]
    U_data : numpy.ndarray
        ความเร็ว [m/s]
    U_inf : float
        ความเร็วกระแสอิสระ [m/s]
    wake_params : dict
        Wake parameters จาก analyze_wake_profile()
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

# ตัวอย่างการใช้งาน
fig, ax = plt.subplots(figsize=(10, 6))
plot_wake_profile(y_coords, U_data, U_inf, wake_params, ax=ax)
plt.tight_layout()
plt.savefig('wake_profile.pdf', dpi=300)
plt.show()
```

---

## 6. การวิเคราะห์สถิติข้อมูล CFD (Statistical Analysis)

### 6.1 การคำนวณค่าเฉลี่ยและการกระจาย

```python
# NOTE: Synthesized by AI - Verify parameters
import numpy as np
import pandas as pd

def analyze_field_statistics(field_data, field_name='U'):
    """
    วิเคราะห์สถิติของฟิลด์ CFD

    Parameters:
    -----------
    field_data : numpy.ndarray
        ข้อมูลฟิลด์ (shape: [n_cells, 3] สำหรับ vector หรือ [n_cells] สำหรับ scalar)
    field_name : str
        ชื่อของฟิลด์สำหรับรายงาน

    Returns:
    --------
    dict
        สถิติของฟิลด์
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
    """พิมพ์สถิติฟิลด์อย่างสวยงาม"""
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

### 6.2 การวิเคราะห์ Histogram และ PDF

```python
# NOTE: Synthesized by AI - Verify parameters
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

def plot_field_distribution(field_data, field_name='U_mag', ax=None):
    """
    พล็อตการกระจายของฟิลด์ (Histogram + PDF)

    Parameters:
    -----------
    field_data : numpy.ndarray
        ข้อมูลฟิลด์ (1D array)
    field_name : str
        ชื่อฟิลด์สำหรับ label
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
    พล็อตข้อมูล Time Series

    Parameters:
    -----------
    time_data : numpy.ndarray
        ข้อมูลเวลา [s]
    variable_data : numpy.ndarray
        ข้อมูลตัวแปร
    variable_name : str
        ชื่อตัวแปรสำหรับ label
    show_rolling_mean : bool
        แสดงค่าเฉลี่ยเคลื่อนที่หรือไม่
    window : int
        ขนาด window สำหรับ rolling mean
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
    พล็อตประวัติ Convergence ของ Solver

    Parameters:
    -----------
    residuals_data : dict
        Dictionary ของ residuals เช่น {'U': [...], 'p': [...]}
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

### 7.2 การวิเคราะห์ FFT (Frequency Domain)

สำหรับการวิเคราะห์ Unsteady Flow เช่น Vortex Shedding:

```python
# NOTE: Synthesized by AI - Verify parameters
from scipy.fft import fft, fftfreq

def analyze_fft(time_data, signal_data, sampling_rate=None):
    """
    วิเคราะห์ FFT ของสัญญาณ

    Parameters:
    -----------
    time_data : numpy.ndarray
        ข้อมูลเวลา [s]
    signal_data : numpy.ndarray
        สัญญาณ (เช่น Lift coefficient vs time)
    sampling_rate : float, optional
        อัตรา sampling [Hz] (ถ้า None จะคำนวณจาก time_data)

    Returns:
    --------
    dict
        FFT results:
        - frequencies: Frequency array [Hz]
        - amplitudes: Amplitude spectrum
        - dominant_freq: Dominant frequency [Hz]
        - dominant_amplitude: Amplitude ที่ dominant frequency
    """

    N = len(signal_data)

    # คำนวณ sampling rate
    if sampling_rate is None:
        dt = np.mean(np.diff(time_data))
        sampling_rate = 1.0 / dt

    # FFT
    fft_values = fft(signal_data)
    amplitudes = 2.0 / N * np.abs(fft_values[0:N//2])
    frequencies = fftfreq(N, 1.0/sampling_rate)[0:N//2]

    # หา dominant frequency (skip DC component at index 0)
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
    พล็อต FFT Spectrum

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

---

## 8. การเปรียบเทียบกรณีศึกษา (Case Comparison)

### 8.1 การพล็อต Multi-Case Comparison

```python
# NOTE: Synthesized by AI - Verify parameters
def plot_multiple_cases(data_dict, x_key, y_key, ax=None,
                        xlabel=None, ylabel=None, title=None,
                        legend_location='best'):
    """
    พล็อตเปรียบเทียบหลายกรณีศึกษา

    Parameters:
    -----------
    data_dict : dict
        Dictionary ของ cases เช่น:
        {
            'Case1': {'x': [...], 'y': [...]},
            'Case2': {'x': [...], 'y': [...]},
            ...
        }
    x_key : str
        ชื่อ key สำหรับ x-axis data
    y_key : str
        ชื่อ key สำหรับ y-axis data
    ax : matplotlib.axes.Axes, optional
        Axes object
    xlabel : str, optional
        Label สำหรับ x-axis
    ylabel : str, optional
        Label สำหรับ y-axis
    title : str, optional
        Plot title
    legend_location : str
        ตำแหน่ง legend

    Returns:
    --------
    matplotlib.axes.Axes
        Axes object ที่พล็อตแล้ว
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

### 8.2 การพล็อต Convergence Study

```python
# NOTE: Synthesized by AI - Verify parameters
def plot_mesh_convergence(mesh_sizes, error_values,
                          quantity_name='Error', ax=None):
    """
    พล็อต Mesh Convergence Study

    Parameters:
    -----------
    mesh_sizes : list or numpy.ndarray
        ขนาด mesh (เช่น number of cells)
    error_values : list or numpy.ndarray
        ค่า error ที่ corresponding
    quantity_name : str
        ชื่อ quantity สำหรับ label
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
# ไฟล์: plot_config.py

import matplotlib.pyplot as plt
import numpy as np

# การตั้งค่าระดับมืออาชีพ
def setup_publication_style():
    """
    ตั้งค่า Matplotlib สำหรับการตีพิมพ์
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
        'axes.unicode_minus': False,  # ใช้ hyphen แทน minus sign

        # Grid settings
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linewidth': 0.5,
        'grid.linestyle': '--',

        # Legend settings
        'legend.frameon': True,
        'legend.framealpha': 0.8,
        'legend.edgecolor': 'gray',

        # LaTeX settings (ถ้าติดตั้ง LaTeX)
        'text.usetex': False,  # ตั้ง True ถ้ามี LaTeX
    })

def save_figure(fig, filename, formats=['pdf', 'png'], dpi=300):
    """
    บันทึกภาพหลาย format

    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        Figure object
    filename : str
        ชื่อไฟล์ (without extension)
    formats : list
        รายการ formats ที่ต้องการบันทึก
    dpi : int
        DPI สำหรับ raster formats
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

# ตัวอย่างการใช้งาน
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

### 9.3 Color Palettes สำหรับ CFD Visualization

> [!WARNING) ข้อควรระวังในการเลือกสี
> - **ใช้ Perceptually Uniform Colormaps** เช่น `viridis`, `plasma`, `cividis`
> - **หลีกเลี่ยง Rainbow Colormap** (jet/rainbow) สำหรับข้อมูล sequential
> - **ใช้ Diverging Colormaps** เช่น `coolwarm`, `RdBu` สำหรับข้อมูลที่มีจุดศูนย์กลางชัดเจน

```python
# NOTE: Synthesized by AI - Verify parameters
def get_cfd_colormap(cmap_type='sequential'):
    """
    คืนค่า Colormap ที่เหมาะสมสำหรับ CFD

    Parameters:
    -----------
    cmap_type : str
        ประเภทของ colormap: 'sequential', 'diverging', 'qualitative'

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

---

## 10. การสร้างรายงานอัตโนมัติ (Automated Reporting)

### 10.1 การสร้าง Multi-Panel Figures

```python
# NOTE: Synthesized by AI - Verify parameters
def create_multipanel_figure(fig_size=(12, 10), nrows=2, ncols=2):
    """
    สร้าง Multi-panel figure สำหรับรายงาน

    Returns:
    --------
    tuple
        (fig, axes) โดย axes เป็น array ของ Axes objects
    """

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols,
                            figsize=fig_size,
                            constrained_layout=True)

    # Flatten axes array ถ้าจำเป็น
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

# ตัวอย่างการใช้งาน
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

### 10.2 การสร้าง PDF Report ด้วย Python

```python
# NOTE: Synthesized by AI - Verify parameters
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

def create_pdf_report(output_filename, case_name, metadata_dict):
    """
    สร้าง PDF Report หลายหน้า

    Parameters:
    -----------
    output_filename : str
        ชื่อไฟล์ PDF output
    case_name : str
        ชื่อกรณีศึกษา
    metadata_dict : dict
        ข้อมูลเมตาดาตา เช่น solver, mesh, ฯลฯ
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

# ตัวอย่างการใช้งาน
metadata = {
    'Solver': 'simpleFoam',
    'Turbulence Model': 'k-omega SST',
    'Mesh Size': '2.5M cells',
    'Reynolds Number': '1e5',
    'Boundary Conditions': 'U_inf = 10 m/s'
}

create_pdf_report('cfd_report.pdf', 'FlowAroundCylinder', metadata)
```

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
    วิเคราะห์ Flow around cylinder

    Parameters:
    -----------
    forces_data : pandas.DataFrame
        ข้อมูล forces vs time
    U_inf : float
        ความเร็วกระแสอิสระ [m/s]
    diameter : float
        เส้นผ่านศูนย์กลางกระบอก [m]
    rho : float
        ความหนาแน่น [kg/m³]

    Returns:
    --------
    dict
        ผลลัพธ์การวิเคราะห์
    """

    results = {}

    # คำนวณ Cd และ Cl
    A_ref = diameter * 1.0  # Unit depth
    Cd = 2 * forces_data['Fx_total'] / (rho * U_inf**2 * A_ref)
    Cl = 2 * forces_data['Fy_total'] / (rho * U_inf**2 * A_ref)

    # ค่าเฉลี่ย
    results['Cd_mean'] = np.mean(Cd[len(Cd)//2:])  # Second half only
    results['Cl_mean'] = np.mean(Cl[len(Cl)//2:])

    # FFT analysis สำหรับ vortex shedding
    time = forces_data['Time'].values
    cl_signal = Cl.values

    fft_results = analyze_fft(time, cl_signal)

    results['shedding_frequency'] = fft_results['dominant_freq']

    # Strouhal number
    results['Strouhal'] = (results['shedding_frequency'] * diameter) / U_inf

    return results
```

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
- [SciPy](https://scipy.org/) - Scientific computing
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

### A.2 Jupyter Notebook Template

```python
# NOTE: Synthesized by AI - Verify parameters
# Jupyter Notebook สำหรับ CFD Analysis

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

---

**END OF DOCUMENT**
