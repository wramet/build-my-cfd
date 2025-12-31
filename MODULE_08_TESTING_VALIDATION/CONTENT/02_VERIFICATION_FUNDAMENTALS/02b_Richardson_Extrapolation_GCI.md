# 02b การประมาณค่าของริชาร์ดสันและดัชนีการลู่เข้าของกริด (Richardson Extrapolation & Grid Convergence Index)

> [!TIP] ทำไมต้อง Richardson Extrapolation และ GCI?
> เมื่อเราไม่มี Analytical Solution (ซึ่งเป็นกรณีปกติของปัญหาจริง) เราสามารถใช้ผลลัพธ์จากเมชที่มีความละเอียดต่างกันเพื่อประมาณค่า "Exact Solution" ทางอ้อมได้ GCI คือมาตรฐานทองคำในการรายงาน Uncertainty จากเมช ช่วยให้เราสามารถรายงานผลลัพธ์พร้อมช่วงความเชื่อมั่น เช่น "ค่า Drag Coefficient อยู่ที่ $0.345 \pm 0.002$"
>
> **🔧 ผลกระทบต่อ OpenFOAM Case:**
> - กระบวนการนี้มีผลโดยตรงต่อการเลือกขนาดเมชใน `system/blockMeshDict` หรือ `system/snappyHexMeshDict`
> - ต้องใช้ Numerical Schemes เดียวกันใน `system/fvSchemes` ทุกเคส
> - ใช้ `forces` functionObject วัดค่าที่สนใจ (Cd, Cl, Nu, etc.)
> - ต้องการ Post-processing ด้วย Python/MATLAB เพื่อคำนวณ GCI

---

## 🎯 Learning Objectives (วัตถุประสงค์การเรียนรู้)

หลังจากศึกษาบทนี้ ผู้เรียนจะสามารถ:

1. **อธิบายหลักการ**ของ Richardson Extrapolation และเงื่อนไขที่จำเป็นในการใช้งาน
2. **คำนวณ Grid Convergence Index (GCI)** จากข้อมูลเมช 3 ขนาดด้วย Python/MATLAB
3. **ตีความผลลัพธ์ GCI** และรายงานค่าความไม่แน่นอนจากเมชอย่างมืออาชีพ
4. **เปรียบเทียบ GCI กับ MMS** และเลือกวิธีที่เหมาะสมกับสถานการณ์
5. **ประยุกต์ใช้งานใน OpenFOAM** ผ่านการตั้งค่า `blockMeshDict`, `snappyHexMeshDict`, และ `forces` functionObject

---

## 2.3 การประมาณค่าของริชาร์ดสัน (Richardson Extrapolation)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Numerics & Linear Algebra (Domain B) และ Meshing (Domain D)
>
> Richardson Extrapolation ใช้กับผลลัพธ์จากเมชหลายขนาด:
> - **เตรียมเมช:** สร้าง 3 เคส (Coarse, Medium, Fine) ใน `constant/polyMesh/`
>   - เปลี่ยนค่า `nx`, `ny`, `nz` ใน `blockMeshDict` หรือ
>   - เปลี่ยน `levels` ใน `snappyHexMeshDict`
> - **รันการจำลอง:** เก็บผลลัพธ์จากแต่ละเมช
> - **วิเคราะห์ข้อมูล:** ใช้ Python/MATLAB ประมาณค่า Exact Solution
> - **ตั้งค่า Schemes:** ต้องใช้ Scheme เดียวกันใน `system/fvSchemes` ทุกเคส
>
> **🔑 คำสำคัญ:** `blockMeshDict`, `snappyHexMeshDict`, `nx`, `ny`, `nz`, `levels`, `refinementLevels`

### 2.3.1 หลักการ (Principles)

สมมติว่าผลเฉลยเชิงตัวเลข $f$ ขึ้นอยู่กับขนาดเมช $h$ ตามสมการ:

$$
f(h) \approx f_{exact} + C \cdot h^p + \mathcal{O}(h^{p+1})
$$

เมื่อเรามีผลลัพธ์จากเมช 2 ขนาดที่มีอัตราส่วนความละเอียด (Grid Refinement Ratio) $r = h_2 / h_1 > 1$ โดยที่ $h_1$ คือเมชละเอียด และ $h_2$ คือเมชหยาบ เราสามารถประมาณค่า $f_{exact}$ ได้ดังนี้:

$$
f_{exact} \approx f_1 + \frac{f_1 - f_2}{r^p - 1}
$$

> [!TIP] เปรียบเหมือนกล้องจุลทรรศน์
> ลองนึกภาพว่าคุณกำลังดูภาพที่พิกเซลแตก (Coarse mesh) และภาพที่ชัดขึ้นเล็กน้อย (Fine mesh) Richardson Extrapolation คือการใช้สมการคณิตศาสตร์เพื่อ "เดา" ว่าภาพที่ชัดที่สุด (Infinite resolution) หน้าตาเป็นอย่างไร

### 2.3.2 เงื่อนไขการใช้งาน (Conditions)

1. **เมชต้องอยู่ในช่วง Asymptotic Range** (ลู่เข้าแล้ว)
2. **อัตราส่วน $r$ ควรจะคงที่** (แนะนำ $r = 2$ หรืออย่างน้อย $\sqrt{2}$)
3. **รูปทรงของเมชต้องคล้ายกัน** (Geometrically Similar)

---

## 2.4 ดัชนีการลู่เข้าของกริด (Grid Convergence Index - GCI)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Numerics & Linear Algebra (Domain B) และ Meshing (Domain D)
>
> GCI คือมาตรฐานทองคำในการรายงาน Uncertainty จากเมช:
> - **เตรียมเมช 3 ขนาด:** แก้ไข `system/blockMeshDict` หรือ `system/snappyHexMeshDict`
>   ```cpp
>   // ใน blockMeshDict
>   nx   20;   // Coarse
>   nx   40;   // Medium
>   nx   80;   // Fine
>   ```
> - **ตั้งค่า Schemes:** ใช้ Scheme เดียวกันใน `system/fvSchemes`:
>   ```cpp
>   d2Schemes  default none;
>   // สำคัญมาก: อย่าเปลี่ยน scheme ข้ามเคส
>   ```
> - **วัดปริมาณที่สนใจ:** ใช้ `forces` functionObject วัด Cd, Cl:
>   ```cpp
>   functions { forces1 { type forces; ... } }
>   ```
> - **คำนวณ GCI:** ใช้ Python/MATLAB กับ output จาก `postProcessing/`
>
> **🔑 คำสำคัญ:** `blockMeshDict`, `snappyHexMeshDict`, `nx`, `d2Schemes`, `forces`, `postProcessing`

GCI เป็นวิธีการมาตรฐานที่นำเสนอโดย Roache เพื่อระบุแถบความผิดพลาด (Error Band) จากผลของเมช ช่วยให้เราสามารถรายงานผลลัพธ์พร้อมช่วงความเชื่อมั่นได้ เช่น "ค่า Drag Coefficient อยู่ที่ $0.345 \pm 0.002$"

### 2.4.1 ขั้นตอนการคำนวณ GCI (GCI Calculation Steps)

**ขั้นตอนที่ 1: เตรียมเมช 3 ขนาด**
$h_1 < h_2 < h_3$ โดยมีอัตราส่วน $r_{21} = h_2/h_1$ และ $r_{32} = h_3/h_2$ (ควร > 1.3)

**ขั้นตอนที่ 2: คำนวณลำดับความแม่นยำปรากฏ (Apparent Order, $p$)**

$$p = \frac{1}{\ln(r_{21})} |\ln| \varepsilon_{32} / \varepsilon_{21} | + q(p)|$$

โดยที่ $\varepsilon_{21} = f_2 - f_1$ และ $\varepsilon_{32} = f_3 - f_2$

**ขั้นตอนที่ 3: คำนวณ GCI**
สำหรับเมชละเอียด (Fine Grid):

$$GCI_{fine} = \frac{F_s \cdot |\varepsilon_{rel}|}{r^p - 1}$$

โดยที่ $\varepsilon_{rel} = \frac{f_2 - f_1}{f_1}$

*   **$F_s$ (Safety Factor)**:
    *   $F_s = 3.0$ สำหรับเมช 2 ขนาด (ไม่แนะนำ)
    *   $F_s = 1.25$ สำหรับเมช 3 ขนาดขึ้นไป

### 2.4.2 ตัวอย่างโค้ด Python สำหรับคำนวณ GCI

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Simulation Control (Domain C)
>
> การใช้ Python คำนวณ GCI ต้องการข้อมูลจาก OpenFOAM:
> - **ไฟล์ input:** อ่านค่าจาก `postProcessing/forces/0/coeffs`
> - **OpenFOAM output format:**
>   ```cpp
>   # Time        Cd          Cl          Cm
>   1000          0.345       0.123       0.045
>   ```
> - **Automation:** สามารถรัน Python script ผ่าน `system/controlDict`:
>   ```cpp
>   functions
>   {
>       runPythonScript
>       {
>           type            coded;
>           functionObjectLibs ("libutilityFunctionObjects.so");
>           code
>           #{
>               system("python3 $FOAM_CASE/scripts/calculate_gci.py");
>           #};
>       }
>   }
>   ```
>
> **🔑 คำสำคัญ:** `postProcessing`, `forces`, `coeffs`, `coded`, `functionObjectLibs`

```python
import numpy as np

def calculate_gci(f1, f2, f3, r=2.0):
    """
    คำนวณ Grid Convergence Index (GCI)
    f1: ผลลัพธ์จากเมชละเอียด (Fine)
    f2: ผลลัพธ์จากเมชปานกลาง (Medium)
    f3: ผลลัพธ์จากเมชหยาบ (Coarse)
    r: อัตราส่วน Grid Refinement
    """
    epsilon21 = f2 - f1
    epsilon32 = f3 - f2

    # ตรวจสอบการลู่เข้า (Convergence Check)
    oscillatory = False
    if epsilon21 * epsilon32 < 0:
        oscillatory = True

    # คำนวณ Apparent Order (p) แบบ Iterative หรือใช้สูตรประมาณ
    # สำหรับ r คงที่:
    p = np.log(abs(epsilon32 / epsilon21)) / np.log(r)

    # คำนวณ GCI สำหรับเมชละเอียด
    Fs = 1.25
    GCI_fine = (Fs * abs((f2 - f1) / f1)) / (r**p - 1)

    return p, GCI_fine, oscillatory

# ตัวอย่างการใช้งาน
Cd_fine = 0.345
Cd_med = 0.352
Cd_coarse = 0.368

p, gci, osc = calculate_gci(Cd_fine, Cd_med, Cd_coarse)

print(f"Apparent Order (p): {p:.2f}")
print(f"GCI (Fine mesh): {gci*100:.2f}%")
print(f"Reported Value: {Cd_fine} +/- {Cd_fine*gci:.4f}")
```

> **📊 ผลลัพธ์ที่คาดหวัง:**
> โค้ดจะคำนวณค่า $p$ ซึ่งควรใกล้เคียงกับ Theoretical Order ของ Scheme (เช่น 2.0) และบอกค่า GCI ซึ่งเป็น % ความไม่แน่นอน

---

## 2.5 สรุปและแนวทางการเลือกวิธี (Summary and Selection Guide)

| สถานการณ์ | วิธีที่แนะนำ | ข้อดี | ข้อเสีย |
| :--- | :--- | :--- | :--- |
| **ทดสอบ Solver ใหม่** | **MMS** | แม่นยำที่สุด, เช็คได้ทุกเทอม | ยากในการสร้าง Analytical Solution ที่ซับซ้อน |
| **ทำโปรเจกต์ทั่วไป** | **GCI (3 Grids)** | เป็นมาตรฐาน, ไม่ต้องรู้ Exact Solution | ต้องรัน 3 เคส, เปลืองทรัพยากร |
| **ทรัพยากรจำกัด** | **2-Grid Check** | เร็ว | ไม่แม่นยำ, บอกค่าความไม่แน่นอนไม่ได้ |

> [!TIP] คำแนะนำจากมืออาชีพ
> สำหรับงานวิจัยหรือวิศวกรรมขั้นสูง **ต้อง** ทำ Grid Convergence Study (GCI) เสมอ มิฉะนั้นผลลัพธ์ของคุณอาจถูกปฏิเสธเนื่องจากไม่ทราบระดับความไม่แน่นอน

---

## 📋 Key Takeaways (สรุปสิ่งสำคัญ)

### 🔑 แนวคิดหลัก (Core Concepts)

1. **Richardson Extrapolation** ใช้ผลลัพธ์จากเมชหลายขนาดประมาณค่า Exact Solution ทางอ้อม ทำงานได้ดีที่สุดเมื่อเมชอยู่ใน **Asymptotic Range**

2. **Grid Convergence Index (GCI)** คือมาตรฐานในการรายงาน **Uncertainty จากเมช** ด้วย Safety Factor ($F_s$) ที่เหมาะสม:
   - $F_s = 1.25$ สำหรับเมช 3 ขนาด (แนะนำ)
   - $F_s = 3.0$ สำหรับเมช 2 ขนาด

3. **เงื่อนไขที่จำเป็น:**
   - เมชต้องมี **Geometric Similarity** (รูปทรงคล้ายกัน)
   - อัตราส่วน Refinement ($r$) ควรคงที่ ($r=2$ หรือ $\sqrt{2}$)
   - ต้องใช้ **Numerical Schemes เดียวกัน** ทุกเคสใน `system/fvSchemes`

### 🆚 GCI vs MMS: เมื่อไหร่ใช้วิธีไหน?

| ด้าน | **GCI (Richardson)** | **MMS** |
| :--- | :--- | :--- |
| **แหล่งที่มาของ Exact Solution** | ประมาณค่าจากเมชหลายขนาด | สร้างขึ้นเอง (Manufactured) |
| **ความแม่นยำ** | ประมาณค่า ใช้จริงได้ | แม่นยำที่สุด เช็คทุกเทอม |
| **ความยากในการตั้งค่า** | ปานกลาง (ต้องเตรียมเมช 3 ขนาด) | สูง (ต้องเขียน Source Terms) |
| **เหมาะกับ** | ปัญหาจริง ที่ไม่มี Analytical Solution | ทดสอบ Solver ใหม่ หรือ Debug Code |
| **มาตรฐานรายงาน** | ใช้กันทั่วไปในงานวิจัย/วิศวกรรม | ใช้ในการพัฒนา Solver |

### 🔧 การนำไปใช้ใน OpenFOAM

**Workflow การทำ GCI:**

1. **เตรียมเมช 3 ขนาด** โดยแก้ไข:
   - `system/blockMeshDict`: เปลี่ยน `nx`, `ny`, `nz`
   - `system/snappyHexMeshDict`: เปลี่ยน `levels`

2. **รันการจำลอง** ด้วย Schemes เดียวกัน:
   ```cpp
   // system/fvSchemes - ต้องเหมือนกันทุกเคส
   d2Schemes  default none;
   ```

3. **เก็บข้อมูล** ด้วย `forces` functionObject:
   ```cpp
   functions { forces1 { type forces; ... } }
   ```

4. **คำนวณ GCI** ด้วย Python/MATLAB จาก `postProcessing/forces/0/coeffs`

5. **รายงานผล** พร้อม Uncertainty:
   ```
   Drag Coefficient: 0.345 ± 0.002 (GCI = 0.6%)
   ```

---

## 🧠 ตรวจสอบความเข้าใจ (Concept Check)

1. **ถาม:** ถ้าคำนวณ GCI แล้วได้ค่า $p$ (Apparent Order) เป็น 0.5 ทั้งที่ใช้ Scheme แบบ Second-order ($p=2$) เกิดจากอะไรได้บ้าง?
   <details>
   <summary>เฉลย</summary>
   <b>ตอบ:</b> อาจเกิดจากหลายสาเหตุ เช่น (1) เมชยังไม่อยู่ใน Asymptotic Range (หยาบเกินไป), (2) มี Discontinuity ในการไหล (เช่น Shock wave) ที่ลด Order ของ Scheme, หรือ (3) มีบั๊กใน Boundary Conditions
   </details>

2. **ถาม:** Safety Factor ($F_s$) ใน GCI มีไว้เพื่ออะไร?
   <details>
   <summary>เฉลย</summary>
   <b>ตอบ:</b> เพื่อเผื่อความไม่แน่นอนในการประมาณค่า เพราะ GCI เป็นเพียงการประมาณการลู่เข้า ไม่ใช่การวัด Error ที่แท้จริง การใช้ $F_s = 1.25$ (สำหรับ 3 grids) หรือ $3.0$ (สำหรับ 2 grids) ช่วยให้กรอบความผิดพลาดที่รายงานมีความระมัดระวัง (Conservative) และน่าเชื่อถือมากขึ้น
   </details>

3. **ถาม:** Richardson Extrapolation ใช้ได้ผลดีที่สุดเมื่อไหร่?
   <details>
   <summary>เฉลย</summary>
   <b>ตอบ:</b> เมื่อเมชอยู่ใน Asymptotic Range คือความละเอียดเพียงพอที่ error จะลดลงตามทฤษฎี และอัตราส่วน refinement (r) คงที่ ซึ่งหมายความว่าเมชต้องมีความละเอียดพอสมควรก่อนที่จะใช้วิธีนี้
   </details>

4. **ถาม:** ควรใช้ GCI หรือ MMS สำหรับการตรวจสอบความถูกต้องของ OpenFOAM case ใหม่?
   <details>
   <summary>เฉลย</summary>
   <b>ตอบ:</b> ขึ้นอยู่กับเป้าหมาย ถ้าเป็น **ปัญหาจริงที่ไม่มี Analytical Solution** (เช่น กรณีศึกษาทางอุตสาหกรรม) ให้ใช้ **GCI** เพราะเป็นวิธีมาตรฐานและใช้งานได้จริง แต่ถ้ากำลัง **ทดสอบ Solver ใหม่** หรือ **Debug numerical schemes** ให้ใช้ **MMS** เพราะให้ความแม่นยำสูงสุดและตรวจสอบได้ทุกเทอมของสมการ
   </details>

5. **ถาม:** ทำไมต้องใช้ Numerical Schemes เดียวกันทุกเคสเมื่อทำ GCI?
   <details>
   <summary>เฉลย</summary>
   <b>ตอบ:</b> เพราะ GCI ตั้งอยู่บนสมมติฐานว่า **Order of Convergence ($p$) คงที่** ถ้าเปลี่ยน Scheme (เช่น จาก Gauss linear 2nd order เป็น Upwind 1st order) ค่า $p$ จะเปลี่ยน ทำให้การคำนวณ GCI ไม่ถูกต้อง ดังนั้นใน `system/fvSchemes` ต้องกำหนด schemes เหมือนกันทุกเคส โดยเฉพาะ `d2Schemes` และ `interpolationSchemes`
   </details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม Verification Fundamentals
- **บทก่อนหน้า:** [02a_Method_of_Manufactured_Solutions_MMS.md](02a_Method_of_Manufactured_Solutions_MMS.md) — ระเบียบวิธีผลิตผลเฉลย
- **บทถัดไป:** [03_OpenFOAM_Architecture.md](03_OpenFOAM_Architecture.md) — สถาปัตยกรรม OpenFOAM สำหรับ Testing