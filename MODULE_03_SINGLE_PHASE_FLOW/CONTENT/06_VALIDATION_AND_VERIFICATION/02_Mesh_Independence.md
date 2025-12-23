# ความเป็นอิสระของ Mesh (Mesh Independence Study)

## 🎯 บทนำ (Introduction)

**ความเป็นอิสระของ Mesh** คือสภาวะที่ผลเฉลยเชิงตัวเลขไม่เปลี่ยนแปลงอย่างมีนัยสำคัญเมื่อเพิ่มความละเอียดของกริด เป็นขั้นตอนที่สำคัญที่สุดในการทำ **Solution Verification** ซึ่งช่วยรับประกันว่าผลลัพธ์ที่ได้ไม่ได้ขึ้นอยู่กับการเลือก Mesh โดยพลการ

---

## 📐 1. วิธีการ Grid Convergence Index (GCI)

GCI เป็นวิธีมาตรฐานที่แนะนำโดย ASME (ASME V&V 20) เพื่อระบุค่าความไม่แน่นอนเชิงตัวเลขจากการแบ่งส่วน (discretization uncertainty) อย่างเป็นระบบ

### 1.1 กระบวนการ Three-Grid Method

ต้องการการจำลองบน Mesh อย่างน้อย 3 ระดับเพื่อให้สามารถวิเคราะห์อันดับการลู่เข้าที่สังเกตได้อย่างแม่นยำ:

| ระดับ Mesh | ขนาดเซลล์ | จำนวนเซลล์ | การใช้งาน |
|------------|-----------|------------|------------|
| หยาบ ($h_1$) | ใหญ่ที่สุด | น้อยที่สุด | การประเมินเบื้องต้น |
| ปานกลาง ($h_2$) | ปานกลาง | ปานกลาง | การตรวจสอบการลู่เข้า |
| ละเอียด ($h_3$) | เล็กที่สุด | มากที่สุด | การประมาณค่าที่แท้จริง |

> [!INFO] **ข้อกำหนดอัตราส่วนการปรับปรุง**
> อัตราส่วนการปรับปรุง $r = h_{coarse}/h_{fine} > 1.3$ เพื่อให้แน่ใจว่าความแตกต่างระหว่าง Mesh มีนัยสำคัญเพียงพอสำหรับการวิเคราะห์

### 1.2 การคำนวณอันดับการลู่เข้า (Observed Order of Accuracy, p)

อันดับการลู่เข้าที่สังเกตได้ $p$ แสดงถึงอัตราที่ผลเฉลยลู่เข้าสู่ค่าที่แท้จริงเมื่อ Mesh ถูกปรับให้ละเอียดขึ้น:

$$p = \frac{\ln\left|\frac{f_3 - f_2}{f_2 - f_1}\right|}{\ln(r)}$$

โดยที่:
- $f_1, f_2, f_3$ คือปริมาณที่สนใจบน Mesh หยาบ, ปานกลาง, และละเอียด ตามลำดับ
- $r$ คืออัตราส่วนการปรับปรุง (refinement ratio)

> [!TIP] **ค่าอันดับการลู่เข้าที่คาดหวัง**
> - **Linear schemes**: $p \approx 1$
> - **Quadratic schemes**: $p \approx 2$
> - **Higher-order schemes**: $p > 2$

### 1.3 Richardson Extrapolation

ใช้ประมาณค่า "ที่แท้จริง" เมื่อขนาดของ Mesh ลู่เข้าสู่ศูนย์ ($h \to 0$):

$$f_{\text{exact}} \approx f_1 + \frac{f_1 - f_2}{r^p - 1}$$

**หลักการ:**
- สมมติว่าความคลาดเคลื่อนลดลงตามกฎอำนาจ: $\varepsilon \propto h^p$
- ใช้ผลลัพธ์จาก Mesh สองระดับเพื่อคาดการณ์ค่าที่ Mesh ละเอียดอนันต์
- ให้ค่าประมาณที่แม่นยำกว่าผลลัพธ์จาก Mesh ใดๆ ที่ใช้จริง

### 1.4 Grid Convergence Index (GCI)

GCI คือการวัดปริมาณความไม่แน่นอนเชิงตัวเลขที่เกิดจากการลู่เข้าของ Grid:

$$\text{GCI}_{\text{fine}} = F_s \frac{|f_1 - f_2|/|f_1|}{r^p - 1} \times 100\%$$

โดยที่:
- $F_s = 1.25$ สำหรับการศึกษาแบบสาม Grid (ใช้ $p$ ที่สังเกตได้)
- $F_s = 3.0$ สำหรับการศึกษาแบบสอง Grid (ใช้ $p$ ทางทฤษฎี)

### 1.5 การตรวจสอบ Asymptotic Range

ผลเฉลยจะอยู่ในช่วงการลู่เข้าแบบ asymptotic เมื่อ:

$$0.9 < \frac{\text{GCI}_{\text{coarse}}}{r^p \cdot \text{GCI}_{\text{fine}}} < 1.1$$

สิ่งนี้ยืนยันว่า:
- การปรับปรุง Mesh ทำงานได้อย่างถูกต้อง
- ความคลาดเคลื่อนกำลังลดลงอย่างเป็นระบบ
- ผลเฉลยกำลังลู่เข้าสู่ค่าที่แท้จริง

---

## 💻 2. การนำไปใช้ใน OpenFOAM

### 2.1 การดึงค่าปริมาณที่สนใจด้วย Function Objects

เราสามารถทำให้การตรวจสอบนี้เป็นอัตโนมัติได้ผ่าน Function Objects เพื่อดึงค่าที่สนใจออกมาวิเคราะห์:

```cpp
// ตัวอย่างการดึงค่าแรงต้าน (Cd) มาศึกษาความลู่เข้า
functions
{
    forces
    {
        type            forces;
        libs            (fieldFunctionObjects);
        patches         (object_surface);
        writeControl    timeStep;
        writeInterval   1;

        // Density for incompressible flow
        rho             rhoInf;
        log             true;
    }

    forceCoeffs
    {
        type            forceCoeffs;
        libs            (fieldFunctionObjects);
        patches         (object_surface);
        writeControl    timeStep;
        writeInterval   1;

        // Lift and drag direction
        liftDir         (0 1 0);
        dragDir         (1 0 0);
        pitchAxis       (0 0 1);

        // Reference dimensions
        magUInf         10.0;
        lRef            1.0;
        Aref            1.0;

        // Fluid properties
        rhoInf          1.0;
    }
}
```

### 2.2 การสร้าง Mesh หลายระดับอัตโนมัติ

```bash
#!/bin/bash
# สคริปต์สร้าง Mesh สามระดับสำหรับการศึกษาความเป็นอิสระ

# สร้างไดเรกทอรีสำหรับแต่ละระดับ Mesh
mkdir -p cases/{coarse,medium,fine}

# สร้าง Mesh หยาบ (r = 1.3)
sed 's/cells (100 100 1);/cells (50 50 1);/' system/blockMeshDict > system/blockMeshDict_coarse
cp system/blockMeshDict_coarse cases/coarse/system/blockMeshDict
blockMesh -case cases/coarse

# สร้าง Mesh ปานกลาง
sed 's/cells (100 100 1);/cells (65 65 1);/' system/blockMeshDict > system/blockMeshDict_medium
cp system/blockMeshDict_medium cases/medium/system/blockMeshDict
blockMesh -case cases/medium

# สร้าง Mesh ละเอียด
cp system/blockMeshDict cases/fine/system/blockMeshDict
blockMesh -case cases/fine
```

### 2.3 การวิเคราะห์ GCI ด้วย Python

```python
#!/usr/bin/env python3
# gci_analysis.py - คำนวณ Grid Convergence Index จากผลลัพธ์ OpenFOAM
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def calculate_gci(f_values, h_values, Fs=1.25):
    """
    Calculate Grid Convergence Index using Richardson extrapolation.

    Parameters
    ----------
    f_values : list[float]
        Quantity of interest values [coarse, medium, fine]
    h_values : list[float]
        Characteristic cell sizes [h_coarse, h_medium, h_fine]
    Fs : float
        Safety factor (1.25 for three grids, 3.0 for two grids)

    Returns
    -------
    dict : Dictionary with convergence metrics
    """
    f1, f2, f3 = f_values  # coarse, medium, fine
    h1, h2, h3 = h_values

    # Refinement ratios
    r12 = h1 / h2
    r23 = h2 / h3

    # Observed order of convergence
    p = np.log(abs((f3 - f2) / (f2 - f1))) / np.log(r23)

    # Richardson extrapolated value
    f_exact = f1 + (f1 - f2) / (r12**p - 1)

    # Relative errors
    epsilon_a12 = abs(f1 - f2) / abs(f1)
    epsilon_a23 = abs(f2 - f3) / abs(f2)

    # GCI values
    GCI12 = Fs * epsilon_a12 / (r12**p - 1)
    GCI23 = Fs * epsilon_a23 / (r23**p - 1)

    # Asymptotic range check
    asymptotic_ratio = GCI12 / (r12**p * GCI23)

    return {
        'order_of_convergence': p,
        'extrapolated_value': f_exact,
        'GCI_coarse': GCI12 * 100,
        'GCI_fine': GCI23 * 100,
        'asymptotic_ratio': asymptotic_ratio,
        'is_asymptotic': 0.9 < asymptotic_ratio < 1.1
    }

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    # อ่านค่าจากผลลัพธ์ OpenFOAM
    mesh_sizes = ['coarse', 'medium', 'fine']
    cell_sizes = [0.02, 0.0154, 0.0118]  # h values
    drag_coefficients = [1.245, 1.198, 1.187]  # Cd values

    # คำนวณ GCI
    results = calculate_gci(drag_coefficients, cell_sizes)

    # แสดงผลลัพธ์
    print("=== Grid Convergence Analysis ===")
    print(f"Order of convergence: p = {results['order_of_convergence']:.3f}")
    print(f"Richardson extrapolation: Cd = {results['extrapolated_value']:.6f}")
    print(f"GCI (coarse grid): {results['GCI_coarse']:.2f}%")
    print(f"GCI (fine grid): {results['GCI_fine']:.2f}%")
    print(f"Asymptotic ratio: {results['asymptotic_ratio']:.3f}")
    print(f"Asymptotic range: {'Yes' if results['is_asymptotic'] else 'No'}")
```

### 2.4 การรวมเข้ากับ Workflow อัตโนมัติ

```python
class MeshConvergenceStudy:
    """
    เครื่องมือศึกษาการลู่เข้าของ Mesh สำหรับ OpenFOAM
    """

    def __init__(self, base_case_dir):
        self.base_case = Path(base_case_dir)
        self.results = []

    def run_simulation(self, mesh_level, n_cells):
        """รันการจำลองสำหรับระดับ Mesh ที่กำหนด"""
        case_dir = self.base_case / f"{mesh_level}_mesh"

        # อัปเดต blockMeshDict
        self._update_mesh_size(case_dir, n_cells)

        # สร้าง Mesh
        subprocess.run(["blockMesh", "-case", str(case_dir)], check=True)

        # รัน Solver
        subprocess.run(["simpleFoam", "-case", str(case_dir)], check=True)

        # ดึงค่าปริมาณที่สนใจ
        cd_value = self._extract_drag_coefficient(case_dir)

        return {
            'mesh_level': mesh_level,
            'n_cells': n_cells,
            'Cd': cd_value
        }

    def analyze_convergence(self):
        """วิเคราะห์การลู่เข้าและคำนวณ GCI"""
        df = pd.DataFrame(self.results)

        if len(df) >= 3:
            f_values = df['Cd'].tolist()
            h_values = (1.0 / df['n_cells']).tolist()  # h ~ 1/sqrt(N)

            gci_results = calculate_gci(f_values, h_values)
            return gci_results

        return None
```

---

## 🧱 3. การตรวจสอบความละเอียดที่ผนัง ($y^+$)

สำหรับแบบจำลองความปั่นป่วน คุณภาพของผลลัพธ์ขึ้นอยู่กับค่า **$y^+$** อย่างมาก ซึ่งเป็นตัวชี้วัดความละเอียดของ Mesh ใกล้ผนัง

### 3.1 นิยามทางคณิตศาสตร์

$$y^+ = \frac{y u_{\tau}}{\nu} = \frac{y \sqrt{\tau_w/\rho}}{\nu}$$

โดยที่:
- $y$ = ระยะห่างตั้งฉากกับผนัง (wall-normal distance)
- $u_{\tau} = \sqrt{\tau_w/\rho}$ = ความเร็วเสียดทาน (friction velocity)
- $\nu$ = ความหนืดจลนศาสตร์ (kinematic viscosity)
- $\tau_w$ = ความเค้นเฉือนที่ผนัง (wall shear stress)
- $\rho$ = ความหนาแน่นของของไหล (fluid density)

### 3.2 ช่วงค่า $y^+$ ที่เหมาะสม

| ประเภทการจำลอง | ช่วง $y^+$ | คำอธิบาย | Wall Function ที่ใช้ |
|------------------|-----------|------------|---------------------|
| **Low-Re Models** | $y^+ < 1$ | แก้ไข viscous sublayer โดยตรง | `nutLowReWallFunction` |
| **Wall Functions** | $30 < y^+ < 300$ | ใช้กฎลอการิทึม | `nutUWallFunction` |
| **Buffer Region** | $1 < y^+ < 30$ | บริเวณเปลี่ยนผ่าน หลีกเลี่ยง | ไม่แนะนำ |
| **High-Re Models** | $y^+ > 300$ | ความละเอียดไม่เพียงพอ | ปรับปรุง Mesh |

> [!WARNING] **ข้อควรระวัง**
> ค่า $y^+$ ในช่วง $1 < y^+ < 30$ เรียกว่า "buffer region" ซึ่งเป็นบริเวณเปลี่ยนผ่านที่ซับซ้อน ทั้ง low-Re models และ wall functions ไม่ทำงานได้ดีในบริเวณนี้ ควรหลีกเลี่ยงให้ได้มากที่สุด

### 3.3 คำสั่งตรวจสอบใน OpenFOAM

```bash
# คำนวณ yPlus สำหรับทุก patch ที่เป็นผนัง
postProcess -func yPlus

# คำนวณความเค้นเฉือนที่ผนัง
postProcess -func wallShearStress

# เขียนสนาม yPlus สำหรับการแสดงผลด้วยภาพ
yPlus

# ตรวจสอบค่าสถิติ
foamDictionary postProcessing/yPlus/0/yPlus.dat
```

### 3.4 การกำหนดค่า Function Object สำหรับ $y^+$

```cpp
// system/controlDict
functions
{
    yPlus
    {
        type            yPlus;
        functionObjectLibs ("libutilityFunctionObjects.so");
        region          region0;
        enabled         true;
        outputControl   outputTime;
        log             true;
        writeFields     true;

        // Optional: write cell values
        writeCellValues yes;
    }

    wallShearStress
    {
        type            wallShearStress;
        functionObjectLibs ("libfieldFunctionObjects.so");
        enabled         true;
        outputControl   outputTime;
        log             true;
        writeFields     true;
    }
}
```

### 3.5 การคำนวณความสูงของเซลล์แรก

สำหรับเป้าหมาย $y^+$ ที่ต้องการ สามารถคำนวณความสูงของเซลล์แรก:

```python
def calculate_first_cell_height(target_y_plus, Re_L, U_inf, L):
    """
    คำนวณความสูงของเซลล์แรกสำหรับเป้าหมาย y+ ที่ต้องการ

    Parameters
    ----------
    target_y_plus : float
        ค่า y+ เป้าหมาย (เช่น 1 สำหรับ low-Re, 30-300 สำหรับ wall functions)
    Re_L : float
        Reynolds number ตามความยาวลักษณะเฉพาะ
    U_inf : float
        ความเร็วกระแสอิสระ
    L : float
        ความยาวลักษณะเฉพาะ

    Returns
    -------
    float : ความสูงของเซลล์แรก (เมตร)
    """
    # สำหรับกรณีทั่วไป ใช้ skin friction coefficient โดยประมาณ
    Cf = 0.075 / (np.log(Re_L) - 2)**2  # สูตร Schoenherr สำหรับ turbulent flat plate

    # คำนวณ friction velocity
    tau_w = 0.5 * Cf * 1.225 * U_inf**2  # สมมติ rho = 1.225 kg/m³
    u_tau = np.sqrt(tau_w / 1.225)

    # ความหนืดจลนศาสตร์
    nu = U_inf * L / Re_L

    # ความสูงของเซลล์แรก
    y_first = target_y_plus * nu / u_tau

    return y_first

# ตัวอย่างการใช้งาน
Re = 1e6
U_inf = 10.0
L = 1.0

# สำหรับ low-Re model (y+ = 1)
y_low_re = calculate_first_cell_height(1.0, Re, U_inf, L)
print(f"First cell height (low-Re): {y_low_re:.6e} m")

# สำหรับ wall function (y+ = 50)
y_wall_func = calculate_first_cell_height(50.0, Re, U_inf, L)
print(f"First cell height (wall function): {y_wall_func:.6e} m")
```

### 3.6 Mesh Quality Metrics สำหรับผนัง

นอกเหนือจากค่า $y^+$ แล้ว ยังมีเมตริกอื่นๆ ที่ต้องตรวจสอบ:

| เมตริก | นิยาม | เป้าหมาย | ความสำคัญ |
|---------|---------|------------|------------|
| **Expansion Ratio** | อัตราส่วนขนาดเซลล์ในทิศทางตั้งฉากผนัง | < 1.2 | การควบคุมความละเอียด |
| **Aspect Ratio** | อัตราส่วนมิติเซลล์ที่ยาวที่สุดต่อสั้นที่สุด | < 1000 (ใกล้ผนัง) | ความเสถียรของการคำนวณ |
| **Non-orthogonality** | ค่าเบี่ยงเบนจากรูปทรงเซลล์ตั้งฉาก | < 70° | ความแม่นยำของการคำนาณ |
| **Skewness** | การวัดการบิดเบี้ยวของรูปทรงเซลล์ | < 0.5 | คุณภาพของผลเฉลย |

---

## ✅ 4. เกณฑ์การยอมรับ (Acceptance Criteria)

### 4.1 เกณฑ์ GCI สำหรับงานต่างๆ

| ประเภทงาน | เกณฑ์ GCI เป้าหมาย | ความละเอียด Mesh ที่แนะนำ |
|-----------|-------------------|-------------------------|
| งานออกแบบวิศวกรรมทั่วไป | GCI < 5% | Medium |
| งานวิจัยตีพิมพ์ | GCI < 2% | Fine |
| กรณีมาตรฐาน (Benchmark) | GCI < 1% | Very Fine |
| งานวิเคราะห์ความปลอดภัย | GCI < 3% | Fine |

### 4.2 การประเมินผลการศึกษา

> [!TIP] **Checklist สำหรับ Mesh Independence Study**
> - [ ] ใช้อย่างน้อย 3 ระดับ Mesh ที่มีอัตราส่วนการปรับปรุง $r > 1.3$
> - [ ] อันดับการลู่เข้าที่สังเกตได้ $p$ มีค่าใกล้เคียงกับค่าทางทฤษฎี
> - [ ] GCI สำหรับ Mesh ละเอียดอยู่ในเกณฑ์ที่ยอมรับได้
> - [ ] อัตราส่วน asymptotic อยู่ในช่วง $0.9 < \text{ratio} < 1.1$
> - [ ] ค่า $y^+$ สอดคล้องกับ turbulence model ที่ใช้

### 4.3 การบันทึกผลการศึกษา

```python
def generate_mesh_independence_report(results, output_file="mesh_independence_report.md"):
    """
    สร้างรายงานสรุปผลการศึกษาความเป็นอิสระของ Mesh
    """
    report = f"""# รายงานการศึกษาความเป็นอิสระของ Mesh

## สรุปผลการศึกษา

| ระดับ Mesh | จำนวนเซลล์ | ค่า Cd | ความคลาดเคลื่อนสัมพัทธ์ |
|------------|-------------|--------|----------------------|
"""

    for i, result in enumerate(results):
        if i == 0:
            report += f"| {result['level']} | {result['cells']} | {result['Cd']:.6f} | - |\n"
        else:
            error = abs(result['Cd'] - results[0]['Cd']) / results[0]['Cd'] * 100
            report += f"| {result['level']} | {result['cells']} | {result['Cd']:.6f} | {error:.2f}% |\n"

    report += f"""
## การวิเคราะห์การลู่เข้า

- **อันดับการลู่เข้าที่สังเกตได้**: $p = {results['order_of_convergence']:.3f}$
- **Richardson Extrapolation**: $C_{{D,exact}} = {results['extrapolated_value']:.6f}$
- **Grid Convergence Index (Fine Mesh)**: {results['GCI_fine']:.2f}%
- **Asymptotic Range**: {'ใช่' if results['is_asymptotic'] else 'ไม่'}

## ข้อสรุป

ผลการศึกษาแสดงว่า Mesh ระดับ **{results['recommended_mesh']}** ให้ผลลัพธ์ที่เป็นอิสระจาก Mesh
เนื่องจาก GCI = {results['GCI_fine']:.2f}% ซึ่งต่ำกว่าเกณฑ์ที่กำหนด
"""

    with open(output_file, 'w') as f:
        f.write(report)

    print(f"รายงานถูกบันทึกที่: {output_file}")
```

---

## 🔗 5. การเชื่อมโยงกับหัวข้ออื่น

- **[[01_V_and_V_Principles]]** - หลักการพื้นฐานของ Verification และ Validation
- **[[03_Experimental_Validation]]** - การทวนสอบผลลัพธ์กับข้อมูลการทดลอง
- **[[04_Error_Estimation]]** - การประมาณค่าความคลาดเคลื่อนใน CFD
- **[[../03_TURBULENCE_MODELING/03_Wall_Treatment]]** - การจัดการบริเวณใกล้ผนัง

---

## 📚 6. แหล่งอ้างอิงเพิ่มเติม

1. Roache, P.J. (1998). *Verification and Validation in Computational Science and Engineering*. Hermosa Publishers.
2. ASME V&V 20-2009. *Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer*.
3. Celik, I.B., et al. (2008). "Procedure for estimation and reporting of uncertainty due to discretization in CFD applications." *Journal of Fluids Engineering*, 130(7).

---

**หัวข้อถัดไป**: [[03_Experimental_Validation]] - การทวนสอบด้วยข้อมูลจากการทดลอง
