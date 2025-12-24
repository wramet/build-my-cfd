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
// Example configuration for extracting drag coefficient (Cd)
// to study mesh convergence in OpenFOAM
// This function object setup monitors forces and calculates
// force coefficients during the simulation

functions
{
    // Force calculation function object
    forces
    {
        // Type identifier for force computation
        type            forces;
        
        // Load required library for field function objects
        libs            (fieldFunctionObjects);
        
        // Apply to specified surface patches
        patches         (object_surface);
        
        // Output frequency control
        writeControl    timeStep;
        writeInterval   1;

        // Density field name for incompressible flow
        // Uses constant density for force calculations
        rho             rhoInf;
        
        // Enable logging to output file
        log             true;
    }

    // Force coefficients calculation function object
    forceCoeffs
    {
        // Type identifier for force coefficient computation
        type            forceCoeffs;
        
        // Load required library for field function objects
        libs            (fieldFunctionObjects);
        
        // Apply to specified surface patches
        patches         (object_surface);
        
        // Output frequency control
        writeControl    timeStep;
        writeInterval   1;

        // Lift direction vector (y-direction in this case)
        liftDir         (0 1 0);
        
        // Drag direction vector (x-direction in this case)
        dragDir         (1 0 0);
        
        // Pitch axis for moment calculations (z-direction)
        pitchAxis       (0 0 1);

        // Freestream velocity magnitude [m/s]
        magUInf         10.0;
        
        // Reference length for non-dimensionalization [m]
        lRef            1.0;
        
        // Reference area for force coefficients [m²]
        Aref            1.0;

        // Freestream fluid density [kg/m³]
        rhoInf          1.0;
    }
}
```

📂 **Source:** `.applications/solvers/multiphase/driftFluxFoam/incompressibleTwoPhaseInteractingMixture/incompressibleTwoPhaseInteractingMixture.C` (ดัดแปลงจากโครงสร้าง Function Objects)

#### คำอธิบายโค้ด (Code Explanation)

**การดึงค่าปริมาณที่สนใจด้วย Function Objects**

โค้ดนี้แสดงการตั้งค่า Function Objects ใน OpenFOAM เพื่อตรวจสอบค่าแรงและสัมประสิทธิ์แรง (Force Coefficients) ซึ่งเป็นปริมาณที่นิยมใช้ในการศึกษาความเป็นอิสระของ Mesh โดยมีรายละเอียดดังนี้:

1. **Function Object แรก (`forces`)**:
   - ใช้คำนวณแรงที่กระทำต่อพื้นผิว (`object_surface`)
   - อ่านความหนาแน่น (`rhoInf`) เพื่อใช้ในการคำนวณแรง
   - บันทึกค่าแรงทุก time step ด้วย `writeInterval: 1`

2. **Function Object ที่สอง (`forceCoeffs`)**:
   - แปลงค่าแรงเป็นสัมประสิทธิ์ไม่มีมิติ (Non-dimensional coefficients)
   - ต้องระบุทิศทางของแรงยก (`liftDir`) และแรงต้าน (`dragDir`)
   - กำหนดความเร็วกระแสอิสระ (`magUInf`), ความยาวอ้างอิง (`lRef`), และพื้นที่อ้างอิง (`Aref`)

#### หลักการสำคัญ (Key Concepts)

- **Function Objects**: กลไกอัตโนมัติใน OpenFOAM สำหรับคำนวณและบันทึกปริมาณที่สนใจระหว่างการจำลอง
- **Force Coefficients**: สัมประสิทธิ์แรงที่ไม่มีมิติ เช่น $C_D$ (Drag Coefficient) และ $C_L$ (Lift Coefficient) ซึ่งเป็นปริมาณที่ใช้กันทั่วไปในการศึกษาความลู่เข้าของ Mesh
- **Reference Values**: ค่าอ้างอิงเช่น `magUInf`, `lRef`, `Aref` จำเป็นสำหรับการทำให้แรงเป็นปริมาณไร้มิติ ซึ่งทำให้สามารถเปรียบเทียบผลลัพธ์จาก Mesh ระดับต่างๆ ได้

### 2.2 การสร้าง Mesh หลายระดับอัตโนมัติ

```bash
#!/bin/bash
# Script to generate three mesh levels for mesh independence study
# This script creates coarse, medium, and fine meshes with refinement ratio > 1.3

# Create directories for each mesh level
mkdir -p cases/{coarse,medium,fine}

# Generate coarse mesh (r = 1.3)
# Modify blockMeshDict to reduce cell count by factor of 2 in each direction
sed 's/cells (100 100 1);/cells (50 50 1);/' system/blockMeshDict > system/blockMeshDict_coarse
cp system/blockMeshDict_coarse cases/coarse/system/blockMeshDict
blockMesh -case cases/coarse

# Generate medium mesh
# Increase cell count from coarse level
sed 's/cells (100 100 1);/cells (65 65 1);/' system/blockMeshDict > system/blockMeshDict_medium
cp system/blockMeshDict_medium cases/medium/system/blockMeshDict
blockMesh -case cases/medium

# Generate fine mesh
# Use the original (finest) mesh configuration
cp system/blockMeshDict cases/fine/system/blockMeshDict
blockMesh -case cases/fine
```

#### คำอธิบายโค้ด (Code Explanation)

**การสร้าง Mesh หลายระดับอัตโนมัติด้วย Bash Script**

สคริปต์นี้ใช้สร้าง Mesh 3 ระดับ (Coarse, Medium, Fine) เพื่อใช้ในการศึกษาความเป็นอิสระของ Mesh โดยมีขั้นตอนดังนี้:

1. **การสร้างไดเรกทอรี**: ใช้ `mkdir -p` สร้างโฟลเดอร์ `cases/coarse`, `cases/medium`, และ `cases/fine` สำหรับเก็บ Mesh แต่ละระดับ

2. **การปรับเปลี่ยน blockMeshDict**:
   - ใช้ `sed` แก้ไขจำนวนเซลล์ใน `system/blockMeshDict`
   - Mesh หยาบ: ลดจำนวนเซลล์เหลือ 50 × 50
   - Mesh ปานกลาง: ปรับเป็น 65 × 65
   - Mesh ละเอียด: ใช้ค่าเดิม 100 × 100

3. **การสร้าง Mesh**: ใช้คำสั่ง `blockMesh` สร้าง Mesh ในแต่ละไดเรกทอรี

#### หลักการสำคัญ (Key Concepts)

- **Refinement Ratio (r)**: อัตราส่วนของขนาดเซลล์ระหว่าง Mesh ระดับต่างๆ ค่าที่แนะนำคือ $r > 1.3$ เพื่อให้เห็นความแตกต่างของผลลัพธ์อย่างชัดเจน
- **Mesh Hierarchy**: การสร้างลำดับชั้นของ Mesh ตั้งแต่หยาบไปละเอียดช่วยให้สามารถวิเคราะห์แนวโน้มของการลู่เข้าได้อย่างมีประสิทธิภาพ
- **Automation**: การใช้สคริปต์ช่วยลดข้อผิดพลาดจากการแก้ไขด้วยมือ และทำให้กระบวนการทำซ้ำได้อย่างสม่ำเสมอ

### 2.3 การวิเคราะห์ GCI ด้วย Python

```python
#!/usr/bin/env python3
"""
Grid Convergence Index (GCI) Analysis Tool for OpenFOAM Results
This script calculates discretization uncertainty using Richardson extrapolation
following ASME V&V 20 standard
"""

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
    # Extract values from input arrays
    f1, f2, f3 = f_values  # coarse, medium, fine
    h1, h2, h3 = h_values

    # Calculate refinement ratios
    r12 = h1 / h2  # Refinement ratio between coarse and medium
    r23 = h2 / h3  # Refinement ratio between medium and fine

    # Calculate observed order of convergence
    # This represents the actual convergence rate observed in the simulation
    p = np.log(abs((f3 - f2) / (f2 - f1))) / np.log(r23)

    # Perform Richardson extrapolation to estimate exact value
    # This estimates the value at zero grid spacing (h → 0)
    f_exact = f1 + (f1 - f2) / (r12**p - 1)

    # Calculate relative errors between grid levels
    epsilon_a12 = abs(f1 - f2) / abs(f1)  # Relative error coarse-medium
    epsilon_a23 = abs(f2 - f3) / abs(f2)  # Relative error medium-fine

    # Calculate Grid Convergence Index for both grid pairs
    GCI12 = Fs * epsilon_a12 / (r12**p - 1)  # GCI for coarse grid
    GCI23 = Fs * epsilon_a23 / (r23**p - 1)  # GCI for fine grid

    # Check asymptotic range condition
    # This verifies that the solution is in the asymptotic convergence range
    asymptotic_ratio = GCI12 / (r12**p * GCI23)

    return {
        'order_of_convergence': p,
        'extrapolated_value': f_exact,
        'GCI_coarse': GCI12 * 100,  # Convert to percentage
        'GCI_fine': GCI23 * 100,    # Convert to percentage
        'asymptotic_ratio': asymptotic_ratio,
        'is_asymptotic': 0.9 < asymptotic_ratio < 1.1
    }


# Example usage
if __name__ == "__main__":
    # Define mesh configurations
    mesh_sizes = ['coarse', 'medium', 'fine']
    
    # Characteristic cell sizes (h values)
    # These can be calculated as h = 1/sqrt(N) for 2D or 1/N^(1/3) for 3D
    cell_sizes = [0.02, 0.0154, 0.0118]
    
    # Drag coefficient values from OpenFOAM simulations
    drag_coefficients = [1.245, 1.198, 1.187]

    # Perform GCI analysis
    results = calculate_gci(drag_coefficients, cell_sizes)

    # Display results
    print("=== Grid Convergence Analysis ===")
    print(f"Order of convergence: p = {results['order_of_convergence']:.3f}")
    print(f"Richardson extrapolation: Cd = {results['extrapolated_value']:.6f}")
    print(f"GCI (coarse grid): {results['GCI_coarse']:.2f}%")
    print(f"GCI (fine grid): {results['GCI_fine']:.2f}%")
    print(f"Asymptotic ratio: {results['asymptotic_ratio']:.3f}")
    print(f"Asymptotic range: {'Yes' if results['is_asymptotic'] else 'No'}")
```

#### คำอธิบายโค้ด (Code Explanation)

**การวิเคราะห์ Grid Convergence Index (GCI) ด้วย Python**

โค้ดนี้เป็นเครื่องมือสำหรับคำนวณความไม่แน่นอนเชิงตัวเลขจากการแบ่งส่วน (Discretization Uncertainty) ตามมาตรฐาน ASME V&V 20 โดยมีองค์ประกอบสำคัญดังนี้:

1. **ฟังก์ชัน `calculate_gci`**:
   - รับค่าปริมาณที่สนใจจาก 3 ระดับ Mesh และขนาดเซลล์เฉลี่ย ($h$)
   - คำนวณอัตราส่วนการปรับปรุง ($r_{12}, r_{23}$) และอันดับการลู่เข้าที่สังเกตได้ ($p$)
   - ใช้ Richardson Extrapolation ประมาณค่าแท้จริง ($f_{exact}$)
   - คำนวณ GCI สำหรับ Mesh หยาบและละเอียด
   - ตรวจสอบว่าผลเฉลยอยู่ใน Asymptotic Range หรือไม่

2. **ตัวอย่างการใช้งาน**:
   - กำหนดขนาดเซลล์และค่า Drag Coefficient จากการจำลอง
   - เรียกใช้ฟังก์ชัน `calculate_gci` และแสดงผลลัพธ์

#### หลักการสำคัญ (Key Concepts)

- **Richardson Extrapolation**: วิธีการประมาณค่าแท้จริงเมื่อ $h \to 0$ โดยใช้ข้อมูลจาก Mesh 2 ระดับขึ้นไป ใช้หลักการที่ว่าความคลาดเคลื่อนลดลงตามกฎอำนาจ $\varepsilon \propto h^p$
- **Grid Convergence Index (GCI)**: ตัวชี้วัดความไม่แน่นอนเชิงตัวเลขที่เกิดจากการลู่เข้าของ Grid คำนวณจากความคลาดเคลื่อนสัมพัทธ์และอัตราส่วนการปรับปรุง
- **Observed Order of Accuracy ($p$)**: อัตราการลู่เข้าจริงที่สังเกตได้จากการจำลอง ควรมีค่าใกล้เคียงกับค่าทางทฤษฎี (เช่น $p \approx 2$ สำหรับสคีมกำลังสอง)
- **Asymptotic Range**: สภาวะที่ความคลาดเคลื่อนลดลงอย่างเป็นระบบตามกฎอำนาจ ตรวจสอบได้จากเงื่อนไข $0.9 < \text{ratio} < 1.1$

### 2.4 การรวมเข้ากับ Workflow อัตโนมัติ

```python
#!/usr/bin/env python3
"""
Automated Mesh Convergence Study Workflow for OpenFOAM
This class automates the process of running simulations at multiple
mesh levels and analyzing convergence using GCI method
"""

import subprocess
from pathlib import Path
import pandas as pd

class MeshConvergenceStudy:
    """
    Tool for studying mesh convergence in OpenFOAM simulations.
    Automates mesh generation, running solver, and extracting results.
    """

    def __init__(self, base_case_dir):
        """Initialize with base case directory path"""
        self.base_case = Path(base_case_dir)
        self.results = []

    def run_simulation(self, mesh_level, n_cells):
        """
        Run simulation for specified mesh level.
        
        Parameters
        ----------
        mesh_level : str
            Identifier for mesh level (e.g., 'coarse', 'medium', 'fine')
        n_cells : int
            Number of cells in each direction for blockMesh
        
        Returns
        -------
        dict : Simulation results including mesh level, cell count, and Cd value
        """
        case_dir = self.base_case / f"{mesh_level}_mesh"

        # Update blockMeshDict with specified cell count
        self._update_mesh_size(case_dir, n_cells)

        # Generate mesh using blockMesh
        subprocess.run(["blockMesh", "-case", str(case_dir)], check=True)

        # Run OpenFOAM solver (simpleFoam in this example)
        subprocess.run(["simpleFoam", "-case", str(case_dir)], check=True)

        # Extract quantity of interest (drag coefficient)
        cd_value = self._extract_drag_coefficient(case_dir)

        return {
            'mesh_level': mesh_level,
            'n_cells': n_cells,
            'Cd': cd_value
        }

    def analyze_convergence(self):
        """
        Analyze convergence and calculate GCI from stored results.
        
        Returns
        -------
        dict : GCI analysis results if at least 3 mesh levels available
        """
        df = pd.DataFrame(self.results)

        if len(df) >= 3:
            f_values = df['Cd'].tolist()
            
            # Characteristic cell size h ~ 1/sqrt(N) for 2D
            h_values = (1.0 / df['n_cells']).tolist()

            gci_results = calculate_gci(f_values, h_values)
            return gci_results

        return None
```

#### คำอธิบายโค้ด (Code Explanation)

**การรวมเข้ากับ Workflow อัตโนมัติสำหรับ Mesh Convergence Study**

โค้ดนี้แสดงการสร้างคลาส `MeshConvergenceStudy` เพื่ออัตโนมัติกระบวนการศึกษาความเป็นอิสระของ Mesh โดยมีความสามารถดังนี้:

1. **การเริ่มต้น (`__init__`)**:
   - รับพาธของ Base Case Directory
   - เตรียม List สำหรับเก็บผลลัพธ์จากแต่ละระดับ Mesh

2. **การรันการจำลอง (`run_simulation`)**:
   - อัปเดต `blockMeshDict` ด้วยจำนวนเซลล์ที่กำหนด
   - สร้าง Mesh ด้วยคำสั่ง `blockMesh`
   - รัน Solver (เช่น `simpleFoam`)
   - ดึงค่าปริมาณที่สนใจ (Drag Coefficient)
   - คืนค่า Dictionary ที่บรรจุผลลัพธ์

3. **การวิเคราะห์การลู่เข้า (`analyze_convergence`)**:
   - แปลงผลลัพธ์เป็น DataFrame
   - คำนวณขนาดเซลล์เฉลี่ย ($h \approx 1/\sqrt{N}$)
   - เรียกใช้ฟังก์ชัน `calculate_gci` ถ้ามีข้อมูลอย่างน้อย 3 ระดับ

#### หลักการสำคัญ (Key Concepts)

- **Workflow Automation**: การอัตโนมัติทั้งกระบวนการช่วยลดความผิดพลาดจากการทำงานซ้ำด้วยมือ และทำให้สามารถทำซ้ำได้อย่างสม่ำเสมอ
- **Python-OpenFOAM Integration**: การใช้ Python เรียกใช้คำสั่ง OpenFOAM ผ่าน `subprocess` ช่วยให้สามารถควบคุมการจำลองและวิเคราะห์ผลลัพธ์ได้อย่างยืดหยุ่น
- **Batch Processing**: การรันการจำลองหลายระดับพร้อมกันหรือต่อเนื่องกันช่วยประหยัดเวลาและทำให้สามารถวิเคราะห์แนวโน้มได้ทันที

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
# Calculate yPlus for all wall patches
postProcess -func yPlus

# Calculate wall shear stress
postProcess -func wallShearStress

# Write yPlus field for visualization
yPlus

# Check statistics from post-processing directory
foamDictionary postProcessing/yPlus/0/yPlus.dat
```

#### คำอธิบายโค้ด (Code Explanation)

**การตรวจสอบค่า $y^+$ ใน OpenFOAM**

คำสั่งเหล่านี้ใช้ตรวจสอบและวิเคราะห์ค่า $y^+$ ซึ่งเป็นตัวชี้วัดความละเอียดของ Mesh ใกล้ผนัง:

1. **`postProcess -func yPlus`**: คำนวณค่า $y^+$ สำหรับทุก Patch ที่เป็นผนังในการจำลอง และบันทึกค่าสถิติ

2. **`postProcess -func wallShearStress`**: คำนวณความเค้นเฉือนที่ผนัง ($\tau_w$) ซึ่งเป็นค่าที่ใช้ในการคำนวณ $y^+$

3. **`yPlus`**: เขียนสนาม $y^+$ เป็นไฟล์สำหรับการแสดงผลด้วยภาพ (Visualization)

4. **`foamDictionary`**: แสดงค่าสถิติ $y^+$ จากไฟล์ที่บันทึกไว้

#### หลักการสำคัญ (Key Concepts)

- **$y^+$ Value**: ค่าไร้มิติที่แสดงระยะห่างจากผนังในหน่วยกำแพง (Wall Units) ใช้ประเมินความละเอียดของ Mesh ใกล้ผนัง
- **Post-processing Functions**: OpenFOAM มี Function Objects สำเร็จรูปสำหรับคำนวณค่า $y^+$ และ Wall Shear Stress โดยอัตโนมัติ
- **Visualization**: การเขียนสนาม $y^+$ ช่วยให้เห็นการกระจายตัวของค่า $y^+$ บนพื้นผิวผนัง ซึ่งช่วยในการปรับปรุง Mesh

### 3.4 การกำหนดค่า Function Object สำหรับ $y^+$

```cpp
// Function object configuration for yPlus calculation
// Place this in system/controlDict to automatically calculate
// yPlus values during the simulation

functions
{
    // yPlus calculation function object
    yPlus
    {
        // Function object type identifier
        type            yPlus;
        
        // Load required utility library
        functionObjectLibs ("libutilityFunctionObjects.so");
        
        // Region to apply calculation (default: region0)
        region          region0;
        
        // Enable/disable this function object
        enabled         true;
        
        // Output control settings
        outputControl   outputTime;
        
        // Enable logging to output file
        log             true;
        
        // Write yPlus field for visualization
        writeFields     true;

        // Optional: write cell-level values (not just patch values)
        writeCellValues yes;
    }

    // Wall shear stress calculation function object
    wallShearStress
    {
        // Function object type identifier
        type            wallShearStress;
        
        // Load required field library
        functionObjectLibs ("libfieldFunctionObjects.so");
        
        // Enable/disable this function object
        enabled         true;
        
        // Output control settings
        outputControl   outputTime;
        
        // Enable logging to output file
        log             true;
        
        // Write wall shear stress field for visualization
        writeFields     true;
    }
}
```

#### คำอธิบายโค้ด (Code Explanation)

**การกำหนดค่า Function Objects สำหรับคำนวณ $y^+$ และ Wall Shear Stress**

โค้ดนี้แสดงการตั้งค่า Function Objects ใน `system/controlDict` เพื่อคำนวณค่า $y^+$ และ Wall Shear Stress โดยอัตโนมัติระหว่างการจำลอง:

1. **Function Object `yPlus`**:
   - คำนวณค่า $y^+$ สำหรับทุก Patch ที่เป็นผนัง
   - เขียนค่า $y^+$ ลงไฟล์ Log และสนามสำหรับ Visualization
   - ตัวเลือก `writeCellValues: yes` ให้เขียนค่า $y^+$ ระดับเซลล์ (ไม่ใช่เฉพาะ Patch)

2. **Function Object `wallShearStress`**:
   - คำนวณความเค้นเฉือนที่ผนัง ($\tau_w$) ซึ่งจำเป็นสำหรับการคำนวณ $y^+$
   - เขียนสนาม Wall Shear Stress สำหรับ Visualization

#### หลักการสำคัญ (Key Concepts)

- **Automatic Monitoring**: การตั้งค่า Function Objects ทำให้สามารถตรวจสอบค่า $y^+$ อัตโนมัติระหว่างการจำลองโดยไม่ต้องรันคำสั่งแยก
- **Patch vs Cell Values**: ค่า $y^+$ ปกติคำนวณที่ระดับ Patch (ผนัง) แต่สามารถเขียนค่าระดับเซลล์ได้ด้วย `writeCellValues: yes`
- **Field Visualization**: การเขียนสนาม $y^+$ และ Wall Shear Stress ช่วยให้เห็นการกระจายตัวของค่าเหล่านี้บนพื้นผิว ซึ่งมีประโยชน์ในการวิเคราะห์

### 3.5 การคำนวณความสูงของเซลล์แรก

```python
#!/usr/bin/env python3
"""
First Cell Height Calculator for Target yPlus Values
This script calculates the required first cell height to achieve
a target y+ value for turbulence modeling
"""

import numpy as np

def calculate_first_cell_height(target_y_plus, Re_L, U_inf, L):
    """
    Calculate first cell height for target y+ value.
    
    Parameters
    ----------
    target_y_plus : float
        Target y+ value (e.g., 1 for low-Re, 30-300 for wall functions)
    Re_L : float
        Reynolds number based on characteristic length
    U_inf : float
        Freestream velocity [m/s]
    L : float
        Characteristic length [m]
    
    Returns
    -------
    float : First cell height [m]
    """
    # Estimate skin friction coefficient using Schoenherr formula
    # for turbulent flow over a flat plate
    Cf = 0.075 / (np.log(Re_L) - 2)**2
    
    # Calculate friction velocity: u_tau = sqrt(tau_w / rho)
    # Wall shear stress: tau_w = 0.5 * Cf * rho * U_inf^2
    rho = 1.225  # Air density at sea level [kg/m³]
    tau_w = 0.5 * Cf * rho * U_inf**2
    u_tau = np.sqrt(tau_w / rho)

    # Calculate kinematic viscosity
    # Re_L = U_inf * L / nu  =>  nu = U_inf * L / Re_L
    nu = U_inf * L / Re_L

    # Calculate first cell height from y+ definition
    # y+ = y * u_tau / nu  =>  y = y+ * nu / u_tau
    y_first = target_y_plus * nu / u_tau

    return y_first


# Example usage
if __name__ == "__main__":
    # Flow conditions
    Re = 1e6      # Reynolds number
    U_inf = 10.0  # Freestream velocity [m/s]
    L = 1.0       # Characteristic length [m]

    # Calculate first cell height for low-Re model (y+ = 1)
    y_low_re = calculate_first_cell_height(1.0, Re, U_inf, L)
    print(f"First cell height (low-Re, y+ = 1): {y_low_re:.6e} m")

    # Calculate first cell height for wall function (y+ = 50)
    y_wall_func = calculate_first_cell_height(50.0, Re, U_inf, L)
    print(f"First cell height (wall function, y+ = 50): {y_wall_func:.6e} m")
```

#### คำอธิบายโค้ด (Code Explanation)

**การคำนวณความสูงของเซลล์แรกเพื่อให้ได้ค่า $y^+$ ที่ต้องการ**

โค้ดนี้ใช้คำนวณความสูงของเซลล์แรกจากผนัง เพื่อให้ได้ค่า $y^+$ ตามเป้าหมายที่กำหนด (เช่น $y^+ = 1$ สำหรับ Low-Re Model หรือ $y^+ = 50$ สำหรับ Wall Functions):

1. **ฟังก์ชัน `calculate_first_cell_height`**:
   - รับค่า $y^+$ เป้าหมาย, Reynolds Number, ความเร็วกระแสอิสระ, และความยาวลักษณะเฉพาะ
   - ประมาณ Skin Friction Coefficient ($C_f$) ด้วยสูตร Schoenherr สำหรับ Turbulent Flat Plate
   - คำนวณ Friction Velocity ($u_\tau$) จาก Wall Shear Stress
   - คำนวณความหนืดจลนศาสตร์ ($\nu$) จาก Reynolds Number
   - ใช้นิยาม $y^+$ คำนวณความสูงของเซลล์แรก: $y = y^+ \cdot \nu / u_\tau$

2. **ตัวอย่างการใช้งาน**:
   - กำหนดเงื่อนไขการไหล (Reynolds Number, ความเร็ว, ความยาว)
   - คำนวณความสูงเซลล์แรกสำหรับ Low-Re Model ($y^+ = 1$)
   - คำนวณความสูงเซลล์แรกสำหรับ Wall Function ($y^+ = 50$)

#### หลักการสำคัญ (Key Concepts)

- **$y^+$ Definition**: $y^+ = y u_\tau / \nu$ เป็นค่าไร้มิติที่แสดงระยะห่างจากผนังในหน่วยกำแพง (Wall Units)
- **Friction Velocity**: $u_\tau = \sqrt{\tau_w/\rho}$ เป็นความเร็วที่ใช้ทำให้ไร้มิติในบริเวณใกล้ผนัง
- **Skin Friction Coefficient**: $C_f$ แสดงสัดส่วนของความเค้นเฉือนที่ผนังต่อความดันพลวัต ใช้ประมาณค่าสำหรับ Turbulent Flow
- **Mesh Design**: การคำนวณนี้ช่วยกำหนดขนาดเซลล์แรกที่เหมาะสมสำหรับ Turbulence Model ที่เลือกใช้

### 3.6 Mesh Quality Metrics สำหรับผนัง

นอกเหนือจากค่า $y^+$ แล้ว ยังมีเมตริกอื่นๆ ที่ต้องตรวจสอบ:

| เมตริก | นิยาม | เป้าหมาย | ความสำคัญ |
|---------|---------|------------|------------|
| **Expansion Ratio** | อัตราส่วนขนาดเซลล์ในทิศทางตั้งฉากผนัง | < 1.2 | การควบคุมความละเอียด |
| **Aspect Ratio** | อัตราส่วนมิติเซลล์ที่ยาวที่สุดต่อสั้นที่สุด | < 1000 (ใกล้ผนัง) | ความเสถียรของการคำนาณ |
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
#!/usr/bin/env python3
"""
Mesh Independence Report Generator
This script creates a comprehensive markdown report
summarizing mesh independence study results
"""

def generate_mesh_independence_report(results, output_file="mesh_independence_report.md"):
    """
    Generate summary report for mesh independence study.
    
    Parameters
    ----------
    results : dict
        Dictionary containing GCI analysis results
    output_file : str
        Output markdown filename
    """
    # Create report header and summary table
    report = f"""# รายงานการศึกษาความเป็นอิสระของ Mesh

## สรุปผลการศึกษา

| ระดับ Mesh | จำนวนเซลล์ | ค่า Cd | ความคลาดเคลื่อนสัมพัทธ์ |
|------------|-------------|--------|----------------------|
"""

    # Populate results table
    for i, result in enumerate(results):
        if i == 0:
            report += f"| {result['level']} | {result['cells']} | {result['Cd']:.6f} | - |\n"
        else:
            error = abs(result['Cd'] - results[0]['Cd']) / results[0]['Cd'] * 100
            report += f"| {result['level']} | {result['cells']} | {result['Cd']:.6f} | {error:.2f}% |\n"

    # Add convergence analysis section
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

    # Write report to file
    with open(output_file, 'w') as f:
        f.write(report)

    print(f"รายงานถูกบันทึกที่: {output_file}")
```

#### คำอธิบายโค้ด (Code Explanation)

**การสร้างรายงานสรุปผลการศึกษาความเป็นอิสระของ Mesh**

โค้ดนี้ใช้สร้างรายงานแบบ Markdown ที่สรุปผลการศึกษาความเป็นอิสระของ Mesh โดยมีรายละเอียดดังนี้:

1. **ฟังก์ชัน `generate_mesh_independence_report`**:
   - สร้างตารางสรุปผลลัพธ์จาก Mesh แต่ละระดับ
   - แสดงความคลาดเคลื่อนสัมพัทธ์ระหว่าง Mesh ระดับต่างๆ
   - บันทึกผลการวิเคราะห์การลู่เข้า (Order of Convergence, Richardson Extrapolation, GCI)
   - สรุปข้อเสนอแนะเกี่ยวกับ Mesh ที่เหมาะสม

2. **รูปแบบรายงาน**:
   - ใช้ Markdown Format ซึ่งอ่านง่ายและแปลงเป็น PDF/HTML ได้
   - แสดงข้อมูลในตารางที่เป็นระบบ
   - ใช้สมการ LaTeX สำหรับปริมาณทางคณิตศาสตร์

#### หลักการสำคัญ (Key Concepts)

- **Documentation**: การบันทึกผลการศึกษาอย่างเป็นระบบสำคัญมากสำหรับงานวิจัยและงานวิศวกรรม
- **Report Structure**: รายงานที่ดีควรประกอบด้วย (1) สรุปผลลัพธ์, (2) การวิเคราะห์การลู่เข้า, (3) ข้อสรุปและข้อเสนอแนะ
- **Reproducibility**: รายงานที่ชัดเจนช่วยให้ผู้อื่นสามารถทำซ้ำและตรวจสอบผลการศึกษาได้

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