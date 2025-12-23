# การทวนสอบด้วยข้อมูลจากการทดลอง (Experimental Validation)

## 📖 บทนำ (Introduction)

**การทวนสอบ (Validation)** คือกระบวนการตรวจสอบว่าแบบจำลองทางคณิตศาสตร์สามารถแสดงความเป็นจริงทางกายภาพได้อย่างแม่นยำหรือไม่ โดยเปรียบเทียบผลการจำลอง CFD กับข้อมูลจากการทดลองหรือผลเฉลยเชิงวิเคราะห์

> [!INFO] ความสำคัญของการทวนสอบ
> การทวนสอบเป็นขั้นตอนสำคัญเพื่อสร้างความมั่นใจว่าแบบจำลอง CFD สามารถทำนายปรากฏการณ์ทางกายภาพได้อย่างถูกต้อง ก่อนนำไปใช้สำหรับการตัดสินใจทางวิศวกรรมที่มีความสำคัญ

**ข้อผิดพลาดในการทวนสอบ**:
$$\epsilon_{\text{model}} = |f_{\text{experimental}} - f_{\text{model}}|$$

โดยที่:
- $f_{\text{experimental}}$ = ปริมาณทางกายภาพที่วัดได้จากการทดลอง
- $f_{\text{model}}$ = การทำนายจากการจำลอง CFD

---

## 🔬 1. กรณีมาตรฐานสำหรับการทวนสอบ (Validation Benchmarks)

OpenFOAM มีเคสตัวอย่างในโฟลเดอร์ `tutorials/` ที่เหมาะสำหรับการทวนสอบความถูกต้องของ Solver และแบบจำลองฟิสิกส์

### 1.1 กรณีทดสอบมาตรฐาน

| กรณีทดสอบ | วัตถุประสงค์ | ฟิสิกส์ที่ตรวจสอบ | เส้นทางใน OpenFOAM |
|-----------|-------------|-----------------|-------------------|
| **Lid-Driven Cavity** | พื้นฐาน Incompressible | การลู่เข้าของ Solver ความดัน | `incompressible/icoFoam/cavity` |
| **Backward-Facing Step** | ความปั่นป่วน | การแยกตัวและการกลับมารวมกันของกระแส | `incompressible/simpleFoam/pitzDaily` |
| **NACA Airfoils** | อากาศพลศาสตร์ | แรงยกและแรงต้านรอบวัตถุ | `incompressible/simpleFoam/airfoil2D` |
| **Turbulent Channel Flow** | ชั้นขอบเขต | พฤติกรรมใกล้ผนังและโปรไฟล์ความเร็ว | `incompressible/pimpleFoam/channel395` |
| **Dam Break** | หลายเฟส | การไหลแบบอิสระของพื้นผิว | `multiphase/interFoam/laminar/damBreak` |

### 1.2 การเลือกกรณีทดสอบที่เหมาะสม

เกณฑ์การเลือกกรณีทดสอบ:
1. **ความเรียบง่าย**: เริ่มจากกรณีที่มีฟิสิกส์ชัดเจน (เช่น การไหลแบบลามินาร์)
2. **ความพร้อมของข้อมูล**: มีข้อมูลอ้างอิงคุณภาพสูง (experimental data หรือ analytical solutions)
3. **ความเกี่ยวข้อง**: กรณีทดสอบควรมีฟิสิกส์ที่เกี่ยวข้องกับปัญหาที่สนใจ
4. **ความสามารถในการเปรียบเทียบ**: มีปริมาณที่วัดได้ชัดเจน (เช่น drag coefficient, reattachment length)

---

## 📊 2. การเปรียบเทียบเชิงปริมาณ (Quantitative Comparison)

การประเมินความแม่นยำของการจำลองต้องใช้ **Error Norms** เพื่อวัดความแตกต่างทั่วทั้งโดเมนอย่างเป็นระบบ

### 2.1 Error Norms หลัก

#### $L_1$ Norm (Average Absolute Error)

วัดค่าเฉลี่ยของความคลาดเคลื่อนสัมบูรณ์:

$$L_1 = \frac{1}{N}\sum_{i=1}^{N}\left|y_{\text{CFD},i} - y_{\text{exp},i}\right|$$

**จุดเด่น:**
- ทนต่อค่าผิดปกติ (outliers)
- ให้น้ำหนักความคลาดเคลื่อนอย่างสม่ำเสมอ
- เหมาะสำหรับการวัดความแม่นยำโดยรวม

#### $L_2$ Norm (Root Mean Square Error)

ให้ค่าการวัด root-mean-square error โดยเน้นความคลาดเคลื่อนที่ใหญ่กว่าอย่างชัดเจน:

$$L_2 = \sqrt{\frac{1}{N}\sum_{i=1}^{N}\left(y_{\text{CFD},i} - y_{\text{exp},i}\right)^2}$$

**จุดเด่น:**
- มักใช้ในการตรวจสอบความถูกต้อง (validation) ของ CFD
- มีความสัมพันธ์ที่ดีกับความถูกต้องของผลเฉลยทั่วโลก
- สะดวกทางคณิตศาสตร์สำหรับการวิเคราะห์ข้อผิดพลาด

#### $L_\infty$ Norm (Maximum Absolute Error)

จับข้อผิดพลาดที่แย่ที่สุด (worst-case error) ทั่วทั้งโดเมน:

$$L_\infty = \max_{i} \left|y_{\text{CFD},i} - y_{\text{exp},i}\right|$$

**จุดเด่น:**
- มีความสำคัญในการประเมินคุณภาพของผลเฉลยเฉพาะที่
- ระบุบริเวณที่ผลเฉลยอาจไม่น่าเชื่อถือ
- เหมาะสำหรับตรวจสอบบริเวณใกล้ความไม่ต่อเนื่องทางเรขาคณิตหรือบริเวณ gradient สูง

### 2.2 เมตริกเสริมที่มีประโยชน์

#### Coefficient of Determination ($R^2$)

วัดสิ่งที่สัดส่วนของความแปรปรวนในข้อมูลทดลองที่ผลเฉลยสามารถอธิบายได้:

$$R^2 = 1 - \frac{\sum_{i=1}^{N} (y_{\text{CFD},i} - y_{\text{exp},i})^2}{\sum_{i=1}^{N} (y_{\text{exp},i} - \bar{y}_{\text{exp}})^2}$$

- **ค่าที่ดี:** ใกล้เคียง 1.0
- **ข้อจำกัด:** ไม่ได้คำนึงถึง systematic bias

#### Root Mean Square Error (RMSE)

วัดขนาดทั่วไปของข้อผิดพลาด:

$$\text{RMSE} = \sqrt{\frac{1}{N}\sum_{i=1}^{N}\left(y_{\text{CFD},i} - y_{\text{exp},i}\right)^2}$$

- ไวต่อค่าเบี่ยงเบนขนาดใหญ่เป็นพิเศษ
- หน่วยเหมือนกับปริมาณที่วัด

#### Mean Absolute Percentage Error (MAPE)

วัดค่าเฉลี่ยของข้อผิดพลาดเป็นเปอร์เซ็นต์:

$$\text{MAPE} = \frac{100\%}{N}\sum_{i=1}^{N}\left|\frac{y_{\text{CFD},i} - y_{\text{exp},i}}{y_{\text{exp},i}}\right|$$

---

## 🛠️ 3. ขั้นตอนการทวนสอบใน OpenFOAM

### 3.1 สกัดข้อมูลจากการจำลอง

OpenFOAM มีเครื่องมือหลากหลายสำหรับสกัดข้อมูลตามตำแหน่งเดียวกับเซ็นเซอร์ในการทดลอง

#### ใช้คำสั่ง `sample`

```bash
# สร้างไฟล์คอนฟิกูรีชันสำหรับการสุ่มข้อมูลตามเส้น
cat > system/sampleDict << EOF
// เส้นที่จะสุ่มตัวอย่าง
sets
(
    // สุ่มตามเส้นตรงในจุดที่กำหนด
    midLine
    {
        type        uniform;
        axis        distance;  // ระยะทางตามเส้น
        start       (0.0 0.05 0.0);  // จุดเริ่มต้น
        end         (1.0 0.05 0.0);   // จุดสิ้นสุด
        nPoints     100;  // จำนวนจุดที่จะสุ่ม
    }
);

// ฟิลด์ที่จะสุ่ม
fields
(
    U
    p
    k
    omega
);

// การตั้งค่าการสุ่ม
interpolationScheme cellPoint;  // การประมาณค่าที่จุด
EOF

# รันการสุ่มข้อมูล
sample -case . -latestTime
```

#### ใช้ `postProcess` กับ function objects

```bash
# ใช้ function object สำหรับสุ่มข้อมูลตามเส้น
postProcess -func "sets(U,p,k,omega)" -latestTime

# คำนวณสถิติของฟิลด์
postProcess -func "fieldAverage(U,p)"
```

### 3.2 การประมาณค่า (Interpolation)

เมื่อเปรียบเทียบกับข้อมูลการทดลอง อาจต้องประมาณค่าผลลัพธ์ CFD ไปยังตำแหน่งเซ็นเซอร์ที่ไม่ตรงกับจุดกริด

```python
#!/usr/bin/env python3
"""การประมาณค่า OpenFOAM ไปยังตำแหน่งเซ็นเซอร์"""
import numpy as np
import pandas as pd
from scipy.interpolate import griddata, LinearNDInterpolator

def interpolate_cfd_to_sensor_locations(cfd_data, sensor_coords, method='linear'):
    """
    ประมาณค่าข้อมูล CFD ไปยังตำแหน่งเซ็นเซอร์

    Parameters
    ----------
    cfd_data : dict
        พจนานุกรมที่มี 'x', 'y', 'z', 'value'
    sensor_coords : array-like
        พิกัดเซ็นเซอร์ [[x1, y1, z1], [x2, y2, z2], ...]
    method : str
        วิธีการประมาณค่า ('linear', 'nearest', 'cubic')

    Returns
    -------
    array
        ค่าที่ประมาณที่ตำแหน่งเซ็นเซอร์
    """
    # จุดกริด CFD
    grid_points = np.column_stack([cfd_data['x'], cfd_data['y'], cfd_data['z']])
    grid_values = cfd_data['value']

    # ประมาณค่าไปยังตำแหน่งเซ็นเซอร์
    interpolated_values = griddata(
        grid_points,
        grid_values,
        sensor_coords,
        method=method,
        fill_value=np.nan
    )

    return interpolated_values

# ตัวอย่างการใช้งาน
cfd_results = {
    'x': [...],  # พิกัด x ของจุดกริด
    'y': [...],  # พิกัด y ของจุดกริด
    'z': [...],  # พิกัด z ของจุดกริด
    'value': [...]  # ค่าความเร็วที่จุดกริด
}

sensor_locations = np.array([
    [0.1, 0.05, 0.0],
    [0.2, 0.05, 0.0],
    # ... เซ็นเซอร์เพิ่มเติม
])

interpolated_velocities = interpolate_cfd_to_sensor_locations(
    cfd_results,
    sensor_locations
)
```

### 3.3 การคำนวณค่าเฉลี่ยทางสถิติ

สำหรับการไหลแบบปั่นป่วน ต้องใช้การหาค่าเฉลี่ยทางสถิติ (statistical averaging) เพื่อเปรียบเทียบกับข้อมูลทดลอง

```cpp
// การตั้งค่า fieldAverage functionObject ใน system/controlDict
functions
{
    fieldAverage1
    {
        type            fieldAverage;
        functionObjectLibs ("libfieldFunctionObjects.so");

        // ฟิลด์ที่จะหาค่าเฉลี่ย
        fields
        (
            U
            p
            k
            omega
        );

        // ประเภทของค่าเฉลี่ย
        mean            on;     // ค่าเฉลี่ย
        prime2Mean      on;     // ค่าเฉลี่ยของส่วนเบี่ยงเบนมาตรฐาน

        // ฐานเวลาสำหรับการหาค่าเฉลี่ย
        base            time;   // ใช้เวลาเป็นฐาน
        window          10;     // หน้าต่างเวลาสำหรับ running average
    }
}
```

### 3.4 การพล็อตกราฟและการเปรียบเทียบ

```python
#!/usr/bin/env python3
"""การสร้างกราฟเปรียบเทียบระหว่าง CFD และข้อมูลการทดลอง"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def plot_validation_comparison(cfd_file, exp_file, output_file,
                               xlabel='Position (m)', ylabel='Velocity (m/s)',
                               title='Velocity Profile Comparison'):
    """
    สร้างกราฟเปรียบเทียบระหว่าง CFD และข้อมูลการทดลอง
    """
    # โหลดข้อมูล
    cfd_data = pd.read_csv(cfd_file, delim_whitespace=True)
    exp_data = pd.read_csv(exp_file, delim_whitespace=True)

    # สร้างกราฟ
    plt.figure(figsize=(10, 6))

    # พล็อตข้อมูล CFD
    plt.plot(cfd_data['x'], cfd_data['U'], 'b-',
             linewidth=2, label='OpenFOAM CFD')

    # พล็อตข้อมูลการทดลองพร้อมแถบความไม่แน่นอน
    if 'uncertainty' in exp_data.columns:
        plt.errorbar(exp_data['x'], exp_data['U'],
                     yerr=exp_data['uncertainty'],
                     fmt='ro', markersize=6, capsize=5,
                     label='Experimental Data', ecolor='red', alpha=0.7)
    else:
        plt.plot(exp_data['x'], exp_data['U'], 'ro',
                 markersize=6, label='Experimental Data')

    # ตกแต่งกราฟ
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)

    # คำนวณและแสดง error metrics
    l2_error = np.sqrt(np.mean((cfd_data['U'].values - exp_data['U'].values)**2))
    mae = np.mean(np.abs(cfd_data['U'].values - exp_data['U'].values))

    plt.text(0.05, 0.95, f'L2 Error: {l2_error:.4f}\nMAE: {mae:.4f}',
             transform=plt.gca().transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    return l2_error, mae
```

---

## ⚠️ 4. ข้อควรระวังและข้อจำกัด

### 4.1 Experimental Uncertainty

> [!WARNING] ข้อมูลจากการทดลองไม่ใช่ค่าที่แน่นอน 100%
> ข้อมูลการทดลองมีช่วงความคลาดเคลื่อน (uncertainty) เสมอ การประเมินความแม่นยำของ CFD ต้องพิจารณาความไม่แน่นอนนี้ด้วย

**แหล่งที่มาของความไม่แน่นอนในการทดลอง:**
- **Measurement errors**: ความคลาดเคลื่อนจากเครื่องมือวัด
- **Facility effects**: ผลกระทบจากสิ่งอำนวยความสะดวกในการทดสอบ
- **Data reduction**: ความคลาดเคลื่อนจากการประมวลผลข้อมูล
- **Flow unsteadiness**: ความไม่คงที่ของการไหล

**เกณฑ์การยอมรับผล CFD:**
หากผล CFD อยู่ในช่วงความไม่แน่นอนของข้อมูลทดลอง ถือว่ายอมรับได้:

$$|y_{\text{CFD}} - y_{\text{exp}}| \leq U_{\text{exp}}$$

โดยที่ $U_{\text{exp}}$ คือความไม่แน่นอนรวมของการทดลอง

### 4.2 Boundary Condition Sensitivity

บางเคสมีความไวต่อค่าเริ่มต้นและเงื่อนไขขอบเขตมาก:

| พารามิเตอร์ | ผลกระทบ | วิธีการจัดการ |
|-------------|---------|--------------|
| **Turbulence Intensity** ที่ทางเข้า | ส่งผลต่อจุดแยกตัวและความยาวรีแทชเมนต์ | ทำ sensitivity study กับค่าต่างๆ |
| **Pressure Outlet** | ส่งผลต่ออัตราการไหลสูง | ใช้ช่องทางที่ยาวพอสมควร |
| **Wall Roughness** | เปลี่ยนโปรไฟล์ความเร็วใกล้ผนัง | ใช้ค่า roughness ที่ตรงกับการทดลอง |

### 4.3 Scale Effects

ความแตกต่างของสเกลระหว่างการทดสอบในห้องปฏิบัติการกับการใช้งานจริง:

- **Reynolds Number differences**: อาจต้องทำการทดลองที่ Re หลายค่าและทำ extrapolation
- **Geometric scaling**: การย่อส่วนอาจไม่สามารถจำลองปรากฏการณ์ทั้งหมดได้
- **Surface roughness scaling**: ความหยาบของพื้นผิวไม่สามารถย่อส่วนได้ตรง

### 4.4 Model Form Uncertainty

ข้อจำกัดของแบบจำลองทางฟิสิกส์:

- **Turbulence model limitations**: แต่ละโมเดลมีข้อจำกัดในบริบทที่ต่างกัน
- **Near-wall treatment**: Wall functions อาจให้ค่าที่ไม่ถูกต้องในกระแสที่ซับซ้อน
- **Multiphase model assumptions**: การสมมติเรื่อง homogeneity หรือ interface sharpness

---

## 📋 5. รายงานผลการทวนสอบ

### 5.1 โครงสร้างรายงานที่ครอบคลุม

รายงานการทวนสอบที่ดีควรประกอบด้วย:

```markdown
# รายงานการทวนสอบความถูกต้อง (Validation Report)

## 1. คำอธิบายปัญหา
- ปัญหาทางกายภาพและการกำหนดสูตรทางคณิตศาสตร์
- เงื่อนไขขอบเขตและพารามิเตอร์ที่ใช้

## 2. วิธีการเชิงตัวเลข
- รูปแบบการแบ่ง Mesh และการตั้งค่า Solver
- การศึกษาความเป็นอิสระของ Mesh

## 3. การตั้งค่าการทดลอง
- แหล่งที่มาของข้อมูลอ้างอิง
- ความไม่แน่นอนในการทดลอง
- ตำแหน่งเซ็นเซอร์และเทคนิคการวัด

## 4. ผลการทวนสอบ
- การเปรียบเทียบกับข้อมูลจากการทดลอง
- กราฟและตารางเปรียบเทียบ
- Error metrics (L1, L2, L∞, R², RMSE, MAPE)

## 5. การวิเคราะห์ความไม่แน่นอน
- การวัดปริมาณแหล่งที่มาของความไม่แน่นอนทั้งหมด
- Sensitivity analysis

## 6. ข้อสรุป
- การประเมินความเหมาะสมของแบบจำลอง
- ข้อจำกัดและขอบเขตการใช้งาน
- ข้อเสนอแนะสำหรับการพัฒนาต่อ
```

### 5.2 ตัวอย่างเทมเพลตรายงานอัตโนมัติ

```python
#!/usr/bin/env python3
"""
generate_validation_report.py - สร้างรายงานการทวนสอบอัตโนมัติ
"""
import pandas as pd
import numpy as np
from datetime import datetime

def generate_validation_report(cfd_data, exp_data, output_file):
    """สร้างรายงานการทวนสอบแบบอัตโนมัติ"""

    # คำนวณ error metrics
    errors = cfd_data['value'].values - exp_data['value'].values

    l1 = np.mean(np.abs(errors))
    l2 = np.sqrt(np.mean(errors**2))
    linf = np.max(np.abs(errors))

    ss_res = np.sum(errors**2)
    ss_tot = np.sum((exp_data['value'].values - np.mean(exp_data['value'].values))**2)
    r2 = 1 - (ss_res / ss_tot)

    rmse = np.sqrt(np.mean(errors**2))
    mape = np.mean(np.abs(errors / exp_data['value'].values)) * 100

    # สร้างรายงาน
    report = f"""# รายงานการทวนสอบความถูกต้อง CFD

**วันที่:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## สรุปผลการทวนสอบ

### เมตริกความคลาดเคลื่อน

| Metric | ค่า | เกณฑ์ที่ยอมรับได้ | สถานะ |
|--------|------|-------------------|--------|
| L1 Norm | {l1:.6e} | < 1.0e-2 | {'✓ผ่าน' if l1 < 1e-2 else '✗ไม่ผ่าน'} |
| L2 Norm (RMSE) | {l2:.6e} | < 1.0e-2 | {'✓ผ่าน' if l2 < 1e-2 else '✗ไม่ผ่าน'} |
| L∞ Norm | {linf:.6e} | < 5.0e-2 | {'✓ผ่าน' if linf < 5e-2 else '✗ไม่ผ่าน'} |
| R² | {r2:.6f} | > 0.95 | {'✓ผ่าน' if r2 > 0.95 else '✗ไม่ผ่าน'} |
| MAPE | {mape:.2f}% | < 10% | {'✓ผ่าน' if mape < 10 else '✗ไม่ผ่าน'} |

### การวิเคราะห์ผลลัพธ์
"""

    # เพิ่มการวิเคราะห์
    if r2 > 0.95:
        report += "- ความสัมพันธ์ระหว่าง CFD และข้อมูลทดลองดีมาก\n"
    elif r2 > 0.90:
        report += "- ความสัมพันธ์ระหว่าง CFD และข้อมูลทดลองอยู่ในระดับดี\n"
    else:
        report += "- ควรตรวจสอบแบบจำลองหรือการตั้งค่า\n"

    if mape < 5:
        report += "- ความแม่นยำของการทำนายดีเยี่ยม\n"
    elif mape < 10:
        report += "- ความแม่นยำของการทำนายอยู่ในระดับยอมรับได้\n"
    else:
        report += "- ควรปรับปรุง Mesh หรือแบบจำลองฟิสิกส์\n"

    report += f"""
## ข้อเสนอแนะ

1. **การปรับปรุง Mesh** {'- ควรปรับปรุง Mesh ให้ละเอียดขึ้น' if l2 > 1e-2 else '- Mesh มีความละเอียดเพียงพอ'}
2. **แบบจำลองฟิสิกส์** {'- ควรพิจารณาเปลี่ยน Turbulence Model' if r2 < 0.95 else '- แบบจำลองเหมาะสมกับปัญหา'}
3. **เงื่อนไขขอบเขต** {'- ควรตรวจสอบความไวของเงื่อนไขขอบเขต' if linf > 5e-2 else '- เงื่อนไขขอบเขตเหมาะสม'}

## บทสรุป

การทวนสอบความถูกต้องของเคสนี้ {'ผ่านเกณฑ์' if all([l1 < 1e-2, l2 < 1e-2, r2 > 0.95, mape < 10]) else 'ไม่ผ่านเกณฑ์'}
ตามเกณฑ์ที่กำหนดไว้

---
*รายงานนี้สร้างขึ้นอัตโนมัติโดย OpenFOAM Validation Pipeline*
"""

    # บันทึกรายงาน
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    return l1, l2, linf, r2, rmse, mape
```

---

## ✅ 6. แนวทางปฏิบัติที่ดีที่สุด

### 6.1 การเลือกกรณีทดสอบ

1. **Start Simple**: เริ่มจากกรณีที่มีผลเฉลยเชิงวิเคราะห์ (analytical solutions) ก่อนกรณีที่ซับซ้อน
2. **Build Complexity**: เพิ่มความซับซ้อนทีละขั้น (เช่น 2D → 3D, ลามินาร์ → ปั่นป่วน)
3. **Document Everything**: เก็บบันทึกรายละเอียดของกิจกรรม V&V ทั้งหมด
4. **Use Multiple Metrics**: ใช้ตัวชี้วัดหลายตัวเพื่อการประเมินที่ครอบคลุม

### 6.2 เกณฑ์การยอมรับผลการทวนสอบ

| การใช้งาน | เกณฑ์ R² | เกณฑ์ MAPE | เกณฑ์ L2 |
|-------------|----------|------------|----------|
| **Engineering Design** | > 0.90 | < 15% | < 0.1 |
| **Research Publications** | > 0.95 | < 10% | < 0.05 |
| **High-Accuracy Validation** | > 0.98 | < 5% | < 0.02 |

### 6.3 การจัดการกับความไม่แน่นอน

1. **Quantify All Sources**: วัดปริมาณทุกแหล่งที่มาของความไม่แน่นอน
2. **Propagate Uncertainties**: ส่งต่อความไม่แน่นอนผ่านห่วงโซ่การวิเคราะห์
3. **Compare with Uncertainty**: ใช้ความไม่แน่นอนเป็นส่วนหนึ่งของเกณฑ์การยอมรับ
4. **Sensitivity Analysis**: วิเคราะห์ความไวของผลลัพธ์ต่อพารามิเตอร์ต่างๆ

---

## 🔗 7. การเชื่อมโยงกับโมดูลอื่น

การทวนสอบความถูกต้องเป็นส่วนสำคัญของ workflow CFD ที่สมบูรณ์:

- **[[02_Mesh_Independence]]**: การศึกษาความเป็นอิสระของ Mesh เป็นขั้นตอนแรกก่อนการทวนสอบ
- **[[01_V_and_V_Principles]]**: หลักการพื้นฐานของการตรวจสอบและการทวนสอบ
- **[[03_Turbulence_Modeling]]**: การเลือกใช้ turbulence model ที่เหมาะสมส่งผลต่อความแม่นยำของการทำนาย
- **[[04_Heat_Transfer]]**: การทวนสอบการถ่ายเทความร้อนต้องใช้ข้อมูลการทดลองเฉพาะทาง

---

**สรุป:** การทวนสอบด้วยข้อมูลจากการทดลองเป็นขั้นตอนสำคัญเพื่อสร้างความมั่นใจในความแม่นยำของแบบจำลอง CFD การใช้เมตริกที่เหมาะสม การจัดการกับความไม่แน่นอน และการรายงานผลอย่างเป็นระบบจะช่วยให้การจำลอง CFD มีความน่าเชื่อถือและสามารถนำไปใช้สำหรับการตัดสินใจทางวิศวกรรมได้อย่างมั่นใจ
