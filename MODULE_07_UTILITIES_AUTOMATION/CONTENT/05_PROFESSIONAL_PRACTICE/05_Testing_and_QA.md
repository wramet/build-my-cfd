# Testing and QA

การทดสอบและประกันคุณภาพ (Testing and Quality Assurance)

> **ลิงก์ที่เกี่ยวข้อง**:
> - ดูภาพรวม Professional Practice → [00_Overview.md](./00_Overview.md)
> - ดู Version Control → [04_Version_Control_Git.md](./04_Version_Control_Git.md)
> - ดู Documentation → [02_Documentation_Standards.md](./02_Documentation_Standards.md)

---

## 📋 บทนำ (Introduction)

ในโลกการทำงานจริง การทำ CFD simulation ให้ "รันผ่าน" นั้นไม่พอ ต้องมั่นใจว่าผลลัพธ์ถูกต้อง (Accuracy) และสามารถทำซ้ำได้ (Reproducibility) **Testing & QA** คือกระบวนการที่แยก "มือสมัครเล่น" ออกจาก "มืออาชีพ"

ในบทนี้คุณจะเรียนรู้:
- **Validation vs Verification**: ต่างกันอย่างไร?
- **Automated Testing**: สร้างระบบทดสอบอัตโนมัติ
- **Grid Convergence**: ตรวจสอบความละเอียด mesh
- **Regression Tests**: มั่นใจว่าการแก้โค้ดไม่ทำลายสิ่งที่ทำงานได้อยู่แล้ว

> [!WARNING] **Real-world Impact**
> ในโครงการอุตสาหกรรม ข้อผิดพลาด CFD อาจนำไปสู่:
> - การออกแบบที่ล้มเหลว (Design Failure)
> - สูญเสียเวลาและเงินลงทุน
> - เสื่อมเสียชื่อเสียง
> **Testing คือประกันคุณภาพที่ป้องกันปัญหาเหล่านี้**

---

## 🎯 วัตถุประสงค์การเรียนรู้ (Learning Objectives)

เมื่อสำเร็จบทนี้ คุณจะสามารถ:

1. **อธิบายความแตกต่างระหว่าง Validation และ Verification**
2. **สร้าง Grid Convergence Study** เพื่อตรวจสอบความละเอียดของ mesh
3. **เขียน Automated Test Scripts** สำหรับทดสอบ OpenFOAM cases
4. **ตรวจสอบผลลัพธ์** เทียบกับ benchmark หรือ experimental data
5. **สร้าง Regression Test Suite** เพื่อมั่นใจว่าการแก้ไขไม่ทำลายสิ่งที่ทำงานได้อยู่แล้ว

---

## 🔍 1. Validation vs Verification

### 1.1 ความแตกต่าง

| แนวคิด | คำถาม | เป้าหมาย | ตัวอย่าง |
|:--------|:--------|:-----------|:---------|
| **Verification** | "Are we solving the equations **correctly**?" | ตรวจสอบว่าโค้ดถูกต้อง | เปรียบเทียบกับ Analytical solution |
| **Validation** | "Are we solving the **right** equations?" | ตรวจสอบว่าโมเดลทางฟิสิกส์ถูกต้อง | เปรียบเทียบกับ Experimental data |

> **[!TIP] จำง่ายๆ**
> - **Verification**: "คำนวณถูกไหม?" (Code check)
> - **Validation**: "โมเดลถูกไหม?" (Physics check)

### 1.2 ตัวอย่างกรณีศึกษา

**Verification Example:**
```bash
# ทดสอบ simpleFoam กับ Flow ในท่อ (Pipe Flow)
# Analytical solution: ค่า f (friction factor) สามารถคำนวณได้จากสมการ
# ทำ Simulation → คำนวณ f → เปรียบเทียบ
```

**Validation Example:**
```bash
# ทดสอบ Airfoil ด้วย turbulent flow
# ทำ Simulation → เปรียบเทียบ Cl, Cd กับ Experimental data จาก Wind tunnel
```

---

## 📊 2. Grid Convergence Study (GCI)

### 2.1 ทำไมต้องทำ GCI?

Mesh ที่หยาบเกินไป → ผลลัพธ์ไม่แม่นยำ
Mesh ที่ละเอียดเกินไป → สิ้นเปลืองเวลาและทรัพยากร
**Grid Convergence** ช่วยหา "จุดพอดี" (Optimal mesh resolution)

### 2.2 ขั้นตอนการทำ GCI

```mermaid
graph TD
    A[1. Create Coarse Mesh<br/>cells: N₁] --> B[2. Run Simulation<br/>get: ϕ₁]
    B --> C[3. Refine Mesh<br/>cells: N₂ = 2N₁]
    C --> D[4. Run Simulation<br/>get: ϕ₂]
    D --> E[5. Refine Again<br/>cells: N₃ = 2N₂]
    E --> F[6. Run Simulation<br/>get: ϕ₃]
    F --> G[7. Calculate GCI<br/>Check convergence]
```

### 2.3 ตัวอย่างการทำ GCI

**สถานการณ์**: ต้องการหาค่า Drag coefficient ($C_d$) ของ Cylinder

```python
# gci_study.py
import pandas as pd
import numpy as np

# ผลลัพธ์จาก 3 mesh resolutions
results = {
    'mesh': ['coarse', 'medium', 'fine'],
    'cells': [50000, 100000, 200000],
    'Cd': [0.85, 0.82, 0.81]  # ค่า Cd ที่ได้
}

df = pd.DataFrame(results)

# คำนวณ Grid Convergence Index (GCI)
r = 2  # refinement ratio (N₂/N₁)

# คำนวณ order of convergence (p)
ϕ1, ϕ2, ϕ3 = df['Cd']
p = np.abs(np.log((ϕ3 - ϕ2) / (ϕ2 - ϕ1)) / np.log(r))

print(f"Order of convergence: p = {p:.2f}")
```

### 2.4 เกณฑ์การตัดสิน

| เงื่อนไข | ความหมาย |
|:---------|:----------|
| **GCI_fine < 5%** | Mesh ละเอียดพอ (Converged) |
| **5% < GCI < 15%** | ควร refine mesh เพิ่ม |
| **GCI > 15%** | Mesh หยาบเกินไป ต้อง refine |

---

## 🤖 3. Automated Testing Framework

### 3.1 ประเภทของ Testing

| Test Type | ขอบเขต | เวลาที่ใช้ | ตัวอย่าง |
|-----------|--------|------------|----------|
| **Unit** | ฟังก์ชันเดียว / Utility | วินาที - นาที | ทดสอบ `checkMesh` |
| **Integration** | หลาย components | นาที - ชั่วโมง | Mesh → Solver → Post-process |
| **System** | Full workflow | ชั่วโมง | ทดสอบ case ตั้งแต่เริ่มจบ |
| **Regression** | ป้องกันการเสีย | ทุกครั้งก่อน commit | เปรียบเทียบกับ baseline |

### 3.2 Allrun with Automatic Check

```bash
#!/bin/bash
# test_allrun.sh - รันและตรวจสอบอัตโนมัติ

cd ${0%/*} || exit 1

# รัน case
./Allrun

# เช็คว่ารันสำเร็จไหม
if [ $? -ne 0 ]; then
    echo "❌ Simulation FAILED!"
    exit 1
fi

# ตรวจสอบ residuals
echo "Checking residuals..."
latest_log=$(ls -t log.* | head -1)
if grep -q "solution singularity" $latest_log; then
    echo "❌ Solution diverged!"
    exit 1
fi

# ตรวจสอบ mesh quality
echo "Checking mesh..."
if ! checkMesh > /dev/null 2>&1; then
    echo "⚠️  Mesh has issues (check log.checkMesh)"
fi

# เปรียบเทียบกับค่าที่คาดหวัง
echo "Validating results..."
if [ -f "expected_results.txt" ]; then
    diff -q expected_results.txt postProcessing/results.txt
    if [ $? -ne 0 ]; then
        echo "⚠️  Results differ from expected!"
    else
        echo "✅ Results match expected!"
    fi
fi

echo "✅ All tests passed!"
```

### 3.3 Automated Test Suite

```bash
#!/bin/bash
# run_all_tests.sh - รันทุก test cases

test_dir="tests"
failed_cases=()
passed=0
failed=0

for case in $test_dir/*/; do
    case_name=$(basename "$case")
    echo "Testing: $case_name"

    # รัน test
    (cd "$case" && ./Allrun > test.log 2>&1)

    # เช็คผล
    if [ $? -eq 0 ]; then
        echo "✅ $case_name PASSED"
        ((passed++))
    else
        echo "❌ $case_name FAILED"
        failed_cases+=("$case_name")
        ((failed++))
    fi
done

echo ""
echo "=========================================="
echo "Test Summary:"
echo "  Passed: $passed"
echo "  Failed: $failed"
echo "=========================================="

if [ $failed -gt 0 ]; then
    echo "Failed cases:"
    for c in "${failed_cases[@]}"; do
        echo "  - $c"
    done
    exit 1
fi
```

### 3.4 ตรวจสอบผลลัพธ์ด้วย Python

```python
# validate_results.py
import pandas as pd
import numpy as np

def validate_forces(case_dir):
    """ตรวจสอบค่าแรงที่ได้"""

    # อ่านผลลัพธ์จาก forces function object
    forces_file = f"{case_dir}/postProcessing/forces/0/forces.dat"
    data = pd.read_csv(forces_file, skiprows=4, sep='\s+',
                      names=['time', 'Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz'])

    # ค่าเฉลี่ย 100 time steps สุดท้าย
    final = data.tail(100)
    Cd_mean = final['Fx'].mean()
    Cd_std = final['Fx'].std()

    print(f"Cd = {Cd_mean:.4f} ± {Cd_std:.4f}")

    # เช็คว่า converged ไหม
    if Cd_std / abs(Cd_mean) < 0.01:  # น้อยกว่า 1%
        print("✅ Forces converged!")
        return True
    else:
        print("❌ Forces NOT converged!")
        return False

# ใช้งาน
validate_forces(".")
```

---

## 📈 4. Regression Testing

### 4.1 คืออะไร?

**Regression Test** = ทดสอบว่า "การเปลี่ยนแปลง" (code update, mesh refinement) ไม่ทำให้ผลลัพธ์ที่เคยถูกต้องกลายเป็นผิดพลาด

### 4.2 สร้าง Baseline Results

```bash
#!/bin/bash
# create_baseline.sh - สร้างผลลัพธ์อ้างอิง

case_dir="baseline_case"

# รัน simulation
(cd $case_dir && ./Allrun)

# บันทึกผลลัพธ์ที่สำคัญ
cp $case_dir/postProcessing/forces/0/forces.dat baseline_forces.dat
cp $case_dir/postProcessing/probes/0/p baseline_pressure.dat

echo "✅ Baseline created!"
```

### 4.3 ทดสอบเทียบกับ Baseline

```python
# regression_test.py
import pandas as pd
import numpy as np

def regression_test(current_file, baseline_file, tolerance=0.02):
    """
    เปรียบเทียบผลลัพธ์ปัจจุบันกับ baseline

    Args:
        tolerance: ค่าที่ยอมรับได้ (default 2%)
    """

    # อ่านข้อมูล
    current = pd.read_csv(current_file, skiprows=4, sep='\s+')
    baseline = pd.read_csv(baseline_file, skiprows=4, sep='\s+')

    # ค่าเฉลี่ยสุดท้าย
    current_val = current.tail(100).mean()
    baseline_val = baseline.tail(100).mean()

    # คำนวณ % difference
    diff = abs((current_val - baseline_val) / baseline_val) * 100

    print(f"Current: {current_val:.4f}")
    print(f"Baseline: {baseline_val:.4f}")
    print(f"Difference: {diff:.2f}%")

    if diff < tolerance * 100:
        print("✅ REGRESSION TEST PASSED")
        return True
    else:
        print(f"❌ REGRESSION TEST FAILED (diff > {tolerance*100}%)")
        return False

# ใช้งาน
regression_test("postProcessing/forces/0/forces.dat",
                "baseline_forces.dat")
```

---

## 🧪 5. การทดสอบ Utility แบบ Unit Test

### 5.1 ทดสอบ Custom Utility

```bash
#!/bin/bash
# test_custom_utility.sh

# สร้าง test case ง่ายๆ
test_case="test_util"
mkdir -p $test_case
cd $test_case

# สร้าง mesh ง่ายๆ
blockMesh > log.blockMesh 2>&1

# รัน custom utility
myCustomUtility > log.utility 2>&1

# ตรวจสอบ output
if [ ! -f "output_field.dat" ]; then
    echo "❌ Utility did not create output!"
    exit 1
fi

# ตรวจสอบค่าที่ผิดปกติ
if grep -q "nan\|inf\|NaN" output_field.dat; then
    echo "❌ Output contains NaN/Inf!"
    exit 1
fi

echo "✅ Unit test passed!"
```

---

## 📋 Quick Reference

| ประเภท | วัตถุประสงค์ | เครื่องมือ |
|:-------|:-------------|:----------|
| **Verification** | ตรวจสอบโค้ดถูกต้อง | Analytical solution, MMS |
| **Validation** | ตรวจสอบฟิสิกส์ถูกต้อง | Experimental data |
| **GCI** | ตรวจสอบ mesh | 3 mesh levels, GCI calculation |
| **Unit Test** | ทดสอบ utility | bash/python test script |
| **Regression** | ป้องกันการเสีย | Baseline comparison |

---

## 📝 แบบฝึกหัด (Exercises)

### ระดับง่าย (Easy)
1. **True/False**: Validation คือการตรวจสอบว่าโค้ดถูกต้อง
   <details>
   <summary>คำตอบ</summary>
   ❌ เท็จ - Validation คือการตรวจสอบว่าโมเดลฟิสิกส์ถูกต้อง (Verification คือการตรวจสอบโค้ด)
   </details>

2. **เลือกตอบ**: GCI (Grid Convergence Index) ใช้ทำอะไร?
   - a) ตรวจสอบว่า mesh ถูกต้อง
   - b) ตรวจสอบว่า mesh ละเอียดพอ
   - c) ตรวจสอบว่า solver ทำงานถูกต้อง
   - d) ตรวจสอบว่า boundary conditions ถูกต้อง
   <details>
   <summary>คำตอบ</summary>
   ✅ b) ตรวจสอบว่า mesh ละเอียดพอ (Grid convergence)
   </details>

### ระดับปานกลาง (Medium)
3. **อธิบาย**: แตกต่างระหว่าง Unit Test และ Integration Test คืออะไร?
   <details>
   <summary>คำตอบ</summary>
   - **Unit Test**: ทดสอบ component เดียว (เช่น utility หนึ่งๆ) แยกจากส่วนอื่น
   - **Integration Test**: ทดสอบการทำงานร่วมกันของหลาย components (mesh + solver + post-process)
   </details>

4. **เขียนสคริปต์**: จงเขียน bash script เพื่อตรวจสอบว่า simulation diverged หรือไม่
   <details>
   <summary>คำตอบ</summary>
   ```bash
   #!/bin/bash
   log_file="log.simpleFoam"

   if grep -q "solution singularity" $log_file; then
       echo "❌ Solution DIVERGED!"
       exit 1
   else
       echo "✅ Simulation converged"
   fi
   ```
   </details>

### ระดับสูง (Hard)
5. **Hands-on**: ทำ Grid Convergence Study กับ Tutorial case (เช่น cavity) โดยสร้าง 3 mesh resolutions และคำนวณ GCI

6. **Project**: สร้าง Regression Test Suite สำหรับ Tutorial case ที่คุณชอบ โดย:
   - สร้าง baseline results
   - เขียน script เปรียบเทียบกับ baseline
   - ทดสอบโดยเปลี่ยน parameter เล็กน้อยแล้วดูว่า test จะ detect ได้หรือไม่

---

## 🧠 Concept Check

<details>
<summary><b>1. Validation และ Verification ต่างกันอย่างไร?</b></summary>

| แนวคิด | คำถาม | เป้าหมาย |
|:--------|:--------|:-----------|
| **Verification** | "คำนวณถูกไหม?" | ตรวจสอบโค้ดถูกต้อง (vs Analytical solution) |
| **Validation** | "โมเดลถูกไหม?" | ตรวจสอบฟิสิกส์ถูกต้อง (vs Experimental data) |

</details>

<details>
<summary><b>2. Grid Convergence Study ทำไมสำคัญ?</b></summary>

**3 เหตุผลหลัก:**
1. **หา mesh resolution ที่เหมาะสม** (ไม่หยาบเกินไป/ละเอียดเกินไป)
2. **ประเมินความแม่นยำ** ของผลลัพธ์
3. **ประหยัดเวลาและทรัพยากร** (ไม่ refine โดยไม่จำเป็น)
</details>

<details>
<summary><b>3. Regression Test ช่วยอะไร?</b></summary>

ช่วย **มั่นใจว่าการเปลี่ยนแปลง** (code update, mesh refinement, boundary condition change) **ไม่ทำลายสิ่งที่ทำงานได้อยู่แล้ว**

ตัวอย่าง: คุณอัปเกรด OpenFOAM version → รัน regression test → ถ้าผ่าน → มั่นใจว่า behavior ยังเหมือนเดิม
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม Professional Practice
- **Project Organization:** [01_Project_Organization.md](01_Project_Organization.md) — โครงสร้างโปรเจกต์
- **Documentation:** [02_Documentation_Standards.md](02_Documentation_Standards.md) — มาตรฐานการเขียนเอกสาร
- **Version Control:** [04_Version_Control_Git.md](04_Version_Control_Git.md) — การใช้ Git