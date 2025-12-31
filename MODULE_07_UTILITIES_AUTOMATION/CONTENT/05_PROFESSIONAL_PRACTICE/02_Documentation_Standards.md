# Documentation Standards

มาตรฐานการเขียนเอกสาร

---

## 🎯 Learning Objectives

เป้าหมายการเรียนรู้ / Learning Objectives

- **อธิบาย** ความสำคัญของเอกสารที่ดีในการวิจัยเชิงซ้ำได้ (reproducible research)
- **ใช้** เทมเพลットมาตรฐานสำหรับการเขียนเอกสารกรณีศึกษา (case documentation)
- **ประยุกต์** แนวทางการเขียนคอมเมนต์โค้ดและรายงานการตรวจสอบความถูกต้อง (validation reports)
- **หลีกเลี่ยง** ข้อผิดพลาดทั่วไปในการเขียนเอกสาร OpenFOAM

---

## Overview

> **Good documentation** = **Reproducible research**

เอกสารที่ดี = งานวิจัยที่สามารถทำซ้ำได้

---

## WHAT: What is Documentation?

เอกสารประกอบด้วยอะไร?

### ประเภทของเอกสาร OpenFOAM

| ประเภท | วัตถุประสงค์ | ตัวอย่าง |
|---------|-------------|---------|
| **README** | เริ่มต้นใช้งานอย่างรวดเร็ว | คำแนะนำการรันโค้ด การติดตั้ง |
| **Case Documentation** | บันทึกการตั้งค่ากรณีศึกษา | พารามิเตอร์เบาะแส/ชั้นขอบ |
| **Code Comments** | อธิบายโค้ด | สูตรคำนวณ ตรรกะ |
| **Validation Report** | รายงานผลการตรวจสอบ | เปรียบเทียบกับข้อมูลอ้างอิง |
| **Technical Note** | บันทึกเทคนิคเฉพาะ | เทคนิคการตาข่าย การปรับแต่ง solver |

---

## WHY: Why Document?

ทำไมต้องเขียนเอกสาร?

### ประโยชน์หลัก

**1. Reproducibility (การทำซ้ำได้)**
- ผู้อื่นสามารถทำซ้ำงานของคุณได้
- คุณเองสามารถกลับมาทำงานเดิมได้ในอนาคต
- หลีกเลี่ยง "it works on my machine" ปัญหา

**2. Knowledge Transfer (การถ่ายทอดความรู้)**
- ทีมงานใหม่เข้าใจงานได้รวดเร็ว
- ลดเวลาฝึกอบรม
- สร้างฐานความรู้องค์กร

**3. Debugging & Validation (การแก้จุดบกพร่องและตรวจสอบ)**
- ติดตามการเปลี่ยนแปลง
- อ้างอิงผลลัพธ์ได้
- ระบุแหล่งที่มาของข้อผิดพลาด

**4. Professionalism (ความเป็นมืออาชีพ)**
- แสดงความใส่ใจในรายละเอียด
- เพิ่มความน่าเชื่อถือ
- สอดคล้องกับมาตรฐานวิชาการ

---

## HOW: How to Document?

วิธีการเขียนเอกสารที่ดี

### 1. Case Documentation Template

เทมเพลตเอกสารกรณีศึกษา

```markdown
# Project: [Case Name]

## Objective / วัตถุประสงค์
- Validate against [reference data]
- Study [parameter] range

## Setup / การตั้งค่า
### Solver & Scheme
- **Solver:** pimpleFoam
- **Schemes:** 
  - Time: Euler implicit
  - Gradient: Gauss linear

### Mesh / ตาข่าย
- **Type:** blockMesh + snappyHexMesh
- **Cells:** 500k
- **Refinement:**
  - Boundary layers: 5 layers, growth rate 1.3
  - Refinement box around cylinder: level 2

### Boundary Conditions / เงื่อนไขขอบ
| Patch | Type | Values |
|-------|------|--------|
| inlet | fixedValue | uniform (1 0 0) |
| outlet | zeroGradient | - |
| walls | noSlip | - |

## Run Commands / คำสั่งรัน
```bash
# Generate mesh
blockMesh
snappyHexMesh -overwrite

# Run simulation
pimpleFoam > log &

# Post-process
paraFoam
```

## Results / ผลลัพธ์
- Convergence history: `log.pimpleFoam`
- Forces: `postProcessing/forces/`
- Visualizations: `plots/`

## Validation / การตรวจสอบความถูกต้อง
- Drag coefficient: Cd = 1.2 (ref: 1.15, error: 4.3%)
- Strouhal number: St = 0.21 (ref: 0.20, error: 5%)
```

### 2. README Template

เทมเพลต README

```markdown
# [Case Name]

## Description / คำอธิบาย
Brief description of the simulation case

## Requirements / ความต้องการ
- OpenFOAM v2312 or later
- Python 3.8+ (for post-processing)
- 4GB RAM minimum

## Installation / การติดตั้ง
```bash
git clone <repository>
cd <case_directory>
```

## Running the Case / การรัน
```bash
./Allrun      # Complete workflow
# OR
./Allclean    # Clean case
./mesh.sh     # Generate mesh only
./solve.sh    # Run solver only
```

## Case Structure / โครงสร้าง
```
.
├── 0/           # Initial conditions
├── constant/    # Mesh, properties
├── system/      # Solver settings
└── Allrun       # Execution script
```

## Results / ผลลัพธ์
See `postProcessing/` directory
- Forces: `postProcessing/forces/0/forces.dat`
- Probes: `postProcessing/probes/0/`
- Plots: `plots/`

## Validation / การตรวจสอบ
Comparison with [reference] shows < 5% error

## Troubleshooting / การแก้ปัญหา
| Issue | Solution |
|-------|----------|
| Divergence | Reduce time step |
| Slow convergence | Check mesh quality |

## References / อ้างอิง
- [Paper citation]
- [Validation data source]
```

### 3. Code Comments

คอมเมนต์โค้ด

#### ✅ Good Examples / ตัวอย่างที่ดี

```cpp
// Calculate turbulent kinetic energy
// k = 0.5 * (u'^2 + v'^2 + w'^2)
// Reference: Wilcox 1998, Turbulence Modeling
volScalarField k = 0.5 * magSqr(UPrime);

// Blending function for SST model
// F1 = tanh(arg4^4)
// where arg4 = min( max(sqrt(k)/(betaStar*omega*d), 500*nu/(d^2*omega)), 4*rho*k/(sigmaOmega2*d^2*CDkomega))
// Blends between k-omega (near wall) and k-epsilon (free stream)
volScalarField F1 = tanh(F1arg);
```

**แนวทางการเขียน:**
- **อธิบาย "ทำไม"** ไม่ใช่ "ทำอะไร" (โค้ดบอกอยู่แล้ว)
- ใส่สูตรคำนวณสำคัญ
- อ้างอิงแหล่งที่มา
- ใช้ภาษาที่ชัดเจน

#### ❌ Bad Examples / ตัวอย่างที่ไม่ดี

```cpp
// Calculate k
volScalarField k = 0.5 * magSqr(UPrime);  // Comment adds no value

// Do the calculation
volScalarField k = 0.5 * magSqr(UPrime);  // Too vague

// This function calculates the turbulent kinetic energy which is 
// defined as half the sum of the squared velocity fluctuations
// in all three directions...
volScalarField k = 0.5 * magSqr(UPrime);  // Too verbose
```

### 4. Validation Report Structure

โครงสร้างรายงานการตรวจสอบความถูกต้อง

```markdown
# Validation Report: [Case Name]

## 1. Objective / วัตถุประสงค์
Validate solver accuracy for [flow configuration]

## 2. Reference Data / ข้อมูลอ้างอิง
- Source: [citation]
- Experimental conditions: Re = [value]
- Uncertainty: ±[value]%

## 3. Methodology / วิธีการ
- Numerical setup: [solver, schemes, mesh]
- Boundary conditions: [description]
- Convergence criteria: [tolerance]

## 4. Results / ผลลัพธ์
| Quantity | OpenFOAM | Reference | Error (%) |
|----------|----------|-----------|-----------|
| Cd | 1.23 | 1.20 | 2.5% |
| Cl (RMS) | 0.45 | 0.47 | 4.3% |
| St | 0.21 | 0.20 | 5.0% |

## 5. Discussion / การอภิปราย
- **Agreement:** Excellent for Cd, good for Cl
- **Discrepancies:** 
  - St difference due to mesh resolution
  - Possible influence of turbulence model
- **Uncertainties:**
  - Experimental: ±2%
  - Numerical: ±1% (mesh, ±0.5% time step)

## 6. Conclusion / สรุป
- **Status:** ✅ PASS - All errors < 5%
- **Recommendations:** 
  - Mesh refinement improves St prediction
  - Case suitable for [application]

## 7. Supporting Data / ข้อมูลเสริม
- Plots: `validation/plots/`
- Mesh statistics: `validation/meshInfo.txt`
- Log files: `validation/logs/`
```

### 5. Anti-Patterns: Common Mistakes

ข้อผิดพลาดทั่วไปที่ควรหลีกเลี่ยง

#### ❌ 1. "Self-Documenting Code" Fallacy

**ข้อผิดพลาด:**
```cpp
void calc() {
    // No comments - "code is self-documenting"
    volScalarField k = 0.5 * magSqr(UPrime);
}
```

**ปัญหา:** อธิบาย "อะไร" แต่ไม่ใช่ "ทำไม"

**วิธีแก้:**
```cpp
// Calculate turbulent kinetic energy for SST model
// Required for turbulence production term
volScalarField k = 0.5 * magSqr(UPrime);
```

#### ❌ 2. Out-of-Sync Documentation

**ข้อผิดพลาด:**
- README บอกใช้ `simpleFoam` แต่จริงใช้ `pimpleFoam`
- รายงาน mesh 500k เซลล์ แต่ไฟล์จริง 1M เซลล์

**วิธีแก้:**
- อัปเดตเอกสารพร้อมกับโค้ด
- ใช้ automated checks (เช่น script ตรวจ mesh info)

#### ❌ 3. "Document Everything"

**ข้อผิดพลาด:**
```cpp
// Set i to 0
int i = 0;
// Increment i
i++;
```

**ปัญหา:** เอกสารมากเกินไป = ไม่มีคนอ่าน

**วิธีแก้:** มุ่งเน้น:
- ตรรกะซับซ้อน
- สูตร/อัลกอริทึมสำคัญ
- การตัดสินใจ (design decisions)

#### ❌ 4. Missing Context

**ข้อผิดพลาย:**
```
## Results
Cd = 1.2
```

**ปัญหา:** ไม่มีบริบท - Re อะไร? เปรียบเทียบกับใคร?

**วิธีแก้:**
```
## Results (Re = 1000)
Cd = 1.2 (ref: 1.15, error: 4.3%)
```

#### ❌ 5. No Validation Summary

**ข้อผิดพลาย:**
```
## Validation
See plots/
```

**ปัญหา:** ผู้อ่านต้องตีความเอง

**วิธีแก้:**
```
## Validation Summary
| Metric | Result | Pass/Fail |
|--------|--------|-----------|
| Cd error < 5% | 4.3% | ✅ |
| St error < 5% | 5.2% | ❌ |
```

---

## 📊 Quick Reference

ตารางอ้างอิงรวดเร็ว

| ประเภทเอกสาร | เนื้อหาหลัก | ความยาว | อัปเดตบ่อยไหม |
|-------------|-----------|---------|---------------|
| **README** | Quick start, การติดตั้ง, การรัน | สั้น (1-2 หน้า) | ✅ ใช่ |
| **Case Doc** | พารามิเตอร์, BC, mesh | ปานกลาง | ✅ ใช่ |
| **Code Comment** | ตรรกะโค้ด, สูตร | สั้น (บรรทัดต่อบรรทัด) | ✅ ใช่ |
| **Validation Report** | ผลเปรียบเทียบ, error metrics | ยาว (5-10 หน้า) | ❌ ไม่ |
| **Technical Note** | เทคนิคเฉพาะทาง | ยาว/สั้น | ❌ ไม่ |

---

## 🎓 Best Practices Summary

สรุปแนวปฏิบัติที่ดี

### ✅ DO / ควรทำ

1. **Document as you code** - เขียนเอกสารพร้อมกับเขียนโค้ด
2. **Use templates** - ใช้เทมเพลตมาตรฐาน
3. **Include context** - ใส่บริบท (เช่น Re, การเปรียบเทียบ)
4. **Add formulas** - ใส่สูตรคำนวณสำคัญ
5. **Reference sources** - อ้างอิงแหล่งที่มา
6. **Keep it current** - อัปเดตเอกสารพร้อมกับโค้ด
7. **Visualize** - ใช้กราฟ/ตารางเมื่อเหมาะสม

### ❌ DON'T / ไม่ควรทำ

1. **Document obvious code** - อย่าอธิบายโค้ดที่ชัดเจนอยู่แล้ว
2. **Write novels** - อย่าเขียนยาวเกินไป
3. **Ignore updates** - อย่าปล่อยให้เอกสารล้าสมัย
4. **Skip validation** - อย่าลืมตรวจสอบความถูกต้อง
5. **Use vague language** - อย่าใช้คำกำกวม ("test the code")
6. **Forget audience** - อย่าลืมพิจารณาผู้อ่าน

---

## 🧠 Concept Check

แบบฝึกหัดทดสอบความเข้าใจ

<details>
<summary><b>1. ทำไมต้องเขียนเอกสาร?</b></summary>

**คำตอบ:**
- **Reproducibility** — ผู้อื่นสามารถทำซ้ำงานได้
- **Knowledge Transfer** — ถ่ายทอดความรู้ให้ทีม
- **Debugging** — ติดตามและแก้ไขข้อผิดพลาด
- **Professionalism** — แสดงความเป็นมืออาชีพ
</details>

<details>
<summary><b>2. เวลาเขียนคอมเมนต์โค้ดควรอธิบายอะไร?</b></summary>

**คำตอบ:** อธิบาย **"ทำไม"** (why) ไม่ใช่ **"ทำอะไร"** (what)
- ✅ "Calculate turbulent kinetic energy for production term"
- ❌ "Calculate k"
</details>

<details>
<summary><b>3. Validation report ควรมีส่วนไหนบ้าง?</b></summary>

**คำตอบ:**
1. **Objective** — ตรวจสอบอะไร
2. **Reference** — ข้อมูลเปรียบเทียบมาจากไหน
3. **Methodology** — ตั้งค่าอย่างไร
4. **Results** — ตัวเลข + error %
5. **Conclusion** — ผ่าน/ไม่ผ่าน
6. **Supporting data** — กราฟ, พลอต, logs
</details>

<details>
<summary><b>4. ข้อผิดพลาดทั่วไปในการเขียนเอกสาร?</b></summary>

**คำตอบ:**
- "Self-documenting code" — ไม่ใส่คอมเมนต์
- เอกสารล้าสมัย — ไม่อัปเดต
- Document everything — ยาวเกินไป
- ไม่มีบริบท — เปรียบเทียบกับอะไร
- ไม่สรุปผล validation — ให้ผู้อ่านตีความเอง
</details>

---

## 📋 Key Takeaways

สรุปสิ่งสำคัญ

1. **Good documentation = Reproducible research**
   - เอกสารที่ดีทำให้งานวิจัยสามารถทำซ้ำได้

2. **เอกสาร 4 ประเภทหลัก:**
   - README (เริ่มต้นใช้งาน)
   - Case Documentation (รายละเอียดกรณีศึกษา)
   - Code Comments (อธิบายตรรกะ)
   - Validation Report (ผลการตรวจสอบ)

3. **เขียน "ทำไม" ไม่ใช่ "ทำอะไร":**
   - โค้ดบอก what อยู่แล้ว
   - คอมเมนต์ควรอธิบาย why และ how

4. **ใช้เทมเพลตมาตรฐาน:**
   - ลดเวลาเขียน
   - สม่ำเสมอทุกไฟล์
   - ครบถ้วนทุกส่วน

5. **หลีกเลี่ยง Anti-Patterns:**
   - อย่าเชื่อว่า "code is self-documenting"
   - อย่าเขียนมากเกินไป
   - อย่าปล่อยให้ล้าสมัย
   - อย่าลืมใส่บริบท

6. **Validation report ต้องมีสรุป:**
   - ตัวเลข error %
   - ผ่าน/ไม่ผ่าน
   - คำแนะนำ

---

## 📖 เอกสารที่เกี่ยวข้อง / Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **การจัดโครงสร้าง:** [01_Project_Structure.md](01_Project_Structure.md)
- **Version Control:** [04_Version_Control_Git.md](04_Version_Control_Git.md)
- **Testing & Validation:** [05_Testing_Framework.md](05_Testing_Framework.md)

---

## 🔗 External Resources

แหล่งข้อมูลภายนอก

- [OpenFOAM Documentation Style Guide](https://develop.openfoam.com/Documentation/)
- [Scientific Paper Writing Guidelines](https://www.nature.com/scientific-reports/guide-to-authors)
- [Reproducible Research Best Practices](https://journals.plos.org/plosone/s/reproducibility)