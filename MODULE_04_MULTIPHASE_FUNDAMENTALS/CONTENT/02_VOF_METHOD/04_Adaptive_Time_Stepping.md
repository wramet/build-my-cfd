# การจัดการเวลาแบบอัตโนมัติ (Adaptive Time Stepping)

> [!TIP] **ทำไม Adaptive Time Stepping ถึงสำคัญ?**
> ในการจำลอง VOF ที่มีการเปลี่ยนแปลงของความเร็วของของไหลอย่างมหาศาล (เช่น เขื่อนแตก คลื่นกระแทก) การกำหนด Time Step คงที่เป็นไปไม่ได้ เพราะ:
> - **ช่วงแรก:** น้ำนิ่ง ($\mathbf{U} \approx 0$) → ใช้ Time Step ใหญ่ได้ (ประหยัดเวลา)
> - **ช่วงกลาง:** น้ำทะลัก ($\mathbf{U}$ สูงมาก) → ต้องลด Time Step ทันที (ป้องกัน Diverge)
> - **ช่วงท้าย:** น้ำเริ่มนิ่ง → ขยาย Time Step กลับมาได้ (ประหยัดเวลาอีกครั้ง)
>
> **Adaptive Time Stepping** ใน OpenFOAM จะคำนวณและปรับ $\Delta t$ อัตโนมัติตามค่า Courant Number เพื่อให้ได้ความสมดุลระหว่าง **ความเสถียร** (Stability) และ **ความเร็วในการคำนวณ** (Computational Efficiency)

ในโลกของ VOF โดยเฉพาะการจำลองเหตุการณ์ที่รุนแรง (เช่น เขื่อนแตก หรือคลื่นกระแทก) ความเร็วของของไหลจะเปลี่ยนแปลงอย่างมหาศาลตลอดเวลา
- **ช่วงแรก:** น้ำนิ่ง ($\mathbf{U} \approx 0$) $\rightarrow$ ใช้ Time Step ใหญ่ได้
- **ช่วงกลาง:** น้ำทะลัก ($\mathbf{U}$ สูงมาก) $\rightarrow$ ต้องลด Time Step ทันทีไม่งั้นระเบิด
- **ช่วงท้าย:** น้ำเริ่มนิ่ง $\rightarrow$ ขยาย Time Step กลับมาได้

การปรับ Time Step ด้วยมือ (Manual) เป็นเรื่องที่เป็นไปไม่ได้ ดังนั้นเราจึงต้องใช้ **Adaptive Time Stepping**

---

## 1. แนวคิดพื้นฐาน: Courant Number ($Co$)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain: Simulation Control (Domain C)**
> - **File:** `system/controlDict`
> - **Keywords:** `maxCo`, `maxAlphaCo`, `adjustTimeStep`
>
> Courant Number ($Co$) คือพารามิเตอร์หลักที่ OpenFOAM ใช้คำนวณ $\Delta t$ ใหม่ในทุก Time Step ค่า $Co$ ที่สูงเกินไป (เช่น > 1.0) จะทำให้ Simulation ไม่เสถียร (Unstable) และอาจ Diverge ได้
>
> **การตั้งค่าที่เหมาะสม:**
> - `maxCo`: 0.8 - 1.0 (สำหรับ Momentum)
> - `maxAlphaCo`: 0.5 - 0.8 (สำหรับ Interface ใน VOF)

หัวใจของการควบคุมเวลาคือตัวเลขไร้มิติที่ชื่อว่า **Courant Number**:

$$ Co = \frac{|\mathbf{U}| \Delta t}{\Delta x} $$

- **ความหมายทางกายภาพ:** ใน 1 Time Step ของไหลเดินทางผ่าน Grid Cell ไปได้กี่ช่อง?
- **กฎเหล็กของ interFoam:** เพื่อความเสถียรและผิวที่คมชัด ควรคุมให้ $Co < 1$
  - แปลว่า "อย่าให้ของไหลวิ่งข้ามเกิน 1 ช่องในหนึ่งก้าวเวลา"

> [!TIP] **Analogy: การขับรถเข้าโค้ง**
> - **$\Delta x$ (ขนาด Mesh):** คือความกว้างถนน
> - **$\mathbf{U}$ (ความเร็ว):** คือความเร็วรถ
> - **$\Delta t$ (เวลาตัดสินใจ):** คือความถี่ที่คุณลืมตาดูถนน
>
> ถ้าคุณขับเร็วมาก ($U$ สูง) บนถนนแคบ ($\Delta x$ เล็ก) คุณต้องลืมตาดูถี่ๆ ($\Delta t$ น้อยๆ) ไม่งั้นคุณจะหลุดโค้ง (Simulation Diverge)!

---

## 2. การตั้งค่าใน `controlDict`

> [!NOTE] **📂 OpenFOAM Context**
> **Domain: Simulation Control (Domain C)**
> - **File:** `system/controlDict`
> - **Keywords:**
>   - `adjustTimeStep yes;` - เปิดใช้งาน Adaptive Time Stepping
>   - `maxCo` - Courant Number สูงสุดสำหรับ Momentum
>   - `maxAlphaCo` - Courant Number สูงสุดสำหรับ Interface (VOF เท่านั้น!)
>   - `maxDeltaT` - ค่า Time Step สูงสุดที่เป็นไปได้
>
> **ตำแหน่งไฟล์:** `your_case/system/controlDict`
>
> **การทำงาน:** เมื่อ `adjustTimeStep yes;` ถูกตั้งค่า OpenFOAM จะ:
> 1. คำนวณ $Co$ จาก Velocity Field ปัจจุบัน
> 2. ปรับ $\Delta t$ ใหม่ตามสูตร: $\Delta t_{new} = \frac{maxCo \cdot \Delta x}{|\mathbf{U}|}$
> 3. ตรวจสอบว่า $\Delta t_{new} < maxDeltaT$

เพื่อเปิดใช้งานระบบอัตโนมัติ ให้ตั้งค่าดังนี้ใน `system/controlDict`:

```cpp
adjustTimeStep  yes;    // เปิดใช้งาน Adaptive Time Stepping

maxCo           1.0;    // เป้าหมาย Courant Number สูงสุดสำหรับการไหล (U)
maxAlphaCo      1.0;    // เป้าหมาย Courant Number สูงสุดสำหรับ Interface (สำคัญ!)

maxDeltaT       1.0;    // ห้ามเกินค่านี้ (กันเหนียว)
```

### `maxCo` vs `maxAlphaCo` ต่างกันอย่างไร?
*   **`maxCo`:** คำนวณจากความเร็วเฉลี่ยของของไหล ($\mathbf{U}$) ทั่งโดเมน ใช้คุมเสถียรภาพของสมการโมเมนตัม
*   **`maxAlphaCo`:** คำนวณเฉพาะบริเวณที่มี **Interface** ($0 < \alpha < 1$)
    *   สำหรับ VOF ค่านี้สำคัญที่สุด! ถ้า Interface วิ่งเร็วเกินกว่าที่ MULES จะจับทัน ผิวจะเบลอหรือเกิดฟองอากาศปลอม
    *   **แนะนำ:** ตั้ง `maxAlphaCo` ให้เท่ากับหรือต่ำกว่า `maxCo` เสมอ (เช่น 0.5 - 0.8 เพื่อความชัวร์)

---

## 3. ปัญหาที่พบบ่อย (Troubleshooting)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain: Simulation Control (Domain C)**
> - **File:** `system/controlDict`, `system/fvSolution`, `constant/polyMesh/blockMeshDict` (mesh quality)
> - **Keywords:**
>   - `maxCo` - ถ้าต่ำเกินไป (เช่น 0.1) จะทำให้ Simulation ช้ามาก
>   - `maxAlphaCo` - ควบคุม Courant Number ที่ Interface
>   - Mesh quality metrics (Skewness, Non-orthogonality) - จาก `checkMesh`
>
> **การวินิจฉัยปัญหา:**
> - **กรณี Time Step ลดลงเรื่อยๆ:** มักเกิดจาก Bad Mesh หรือ Spurious Velocity
> - **กรณี Simulation ช้า:** อาจตั้ง `maxCo` ต่ำเกินไป
>
> **เครื่องมือช่วยวินิจฉัย:**
> - `checkMesh` - ตรวจสอบคุณภาพ Mesh
> - `foamListTimes` - ดู Time Step ที่ถูกเขียน
> - Log file - ตรวจสอบค่า Co ในแต่ละ Time Step

### Q: Time step ลดลงเรื่อยๆ จนเหลือ $10^{-20}$ แก้ยังไง?
**สาเหตุ:** มักเกิดจาก "Bad Mesh" หรือความเร็วที่ระเบิดผิดปกติ (Spurious Velocity)
**วิธีแก้:**
1.  **Check Mesh:** ดูค่า Skewness หรือ Non-orthogonality
2.  **Limit Velocity:** ใช้ `fvOptions` เพื่อจำกัดความเร็วสูงสุด (`velocityDamping`) ไม่ให้เกินจริง
3.  **Relaxation:** ปรับลด Relaxation factor ใน `fvSolution`

### Q: Simulation ช้ามาก แต่ $Co$ ยังต่ำอยู่?
**สาเหตุ:** อาจตั้ง `maxCo` ต่ำเกินความจำเป็น (เช่น 0.1)
**วิธีแก้:** ลองขยับ `maxCo` ขึ้นมาเป็น 0.8 - 1.0 (interFoam สมัยใหม่ทนทานพอสมควร)

---

## 4. Sub-cycling กับ Time Step

> [!NOTE] **📂 OpenFOAM Context**
> **Domain: Numerical Methods & Solver Control (Domain B)**
> - **File:** `system/fvSolution`
> - **Keywords:**
>   - `nAlphaSubCycles` - จำนวน Sub-cycles สำหรับสมการ Alpha
>   - `nOuterCorrectors` - จำนวน Outer Correctors ใน PIMPLE
>
> **ตำแหน่งไฟล์:** `your_case/system/fvSolution`
>
> **การทำงาน:** Sub-cycling ช่วยแก้สมการ Alpha (Interface) หลายครั้งภายใน 1 Time Step ของ Momentum:
> - ถ้า `nAlphaSubCycles 3` และ $\Delta t = 0.03$ วินาที
> - สมการ Alpha จะถูกแก้ 3 ครั้ง ด้วย $\Delta t_{sub} = 0.01$ วินาที
> - ทำให้ $Co_{\alpha}$ ลดลง 3 เท่า แต่ Momentum ยังใช้ $\Delta t = 0.03$
>
> **ข้อดี:** เพิ่มความเสถียรของ Interface โดยไม่ต้องลด Time Step ทั้งหมด

อย่างที่กล่าวในบทที่ผ่านมา การใช้ **Sub-cycling** (`nAlphaSubCycles`) ช่วยให้เรา "โกง" ได้นิดหน่อย:

- ถ้า `nAlphaSubCycles 3` เราอาจปล่อยให้ $Co$ ของ Momentum ขึ้นไปถึง 1.5 - 2.0 ได้ (ถ้าจำเป็น)
- เพราะสมการ Alpha จะถูกแก้ด้วย $\Delta t_{sub} = \Delta t / 3$
- ทำให้ $Co_{\alpha}$ ที่แท้จริงเหลือแค่ $2.0 / 3 = 0.66$ (ซึ่งปลอดภัย!)

---

## 5. สรุปสูตรสำเร็จ (Best Practice Settings)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain: Simulation Control (Domain C)**
> - **Files:**
>   - `system/controlDict` - สำหรับ `adjustTimeStep`, `maxCo`, `maxAlphaCo`, `maxDeltaT`
>   - `system/fvSolution` - สำหรับ `nAlphaSubCycles`
> - **Keywords:**
>   - `adjustTimeStep yes;` - เปิด Adaptive Time Stepping
>   - `maxCo 0.8;` - Courant Number สูงสุดสำหรับ Momentum
>   - `maxAlphaCo 0.5;` - Courant Number สูงสุดสำหรับ Interface
>   - `nAlphaSubCycles 2;` - จำนวน Sub-cycles สำหรับ Alpha
>
> **ตัวอย่างการตั้งค่าใน controlDict:**
> ```cpp
> application     interFoam;
> startFrom       latestTime;
>
> adjustTimeStep  yes;
> maxCo           0.8;
> maxAlphaCo      0.5;
> maxDeltaT       1.0;
>
> deltaT          1e-6;  // เริ่มต้นเล็กๆ
> ```
>
> **ตัวอย่างการตั้งค่าใน fvSolution:**
> ```cpp
> solvers
> {
>     "alpha.*"
>     {
>         nAlphaSubCycles 2;
>         // ...
>     }
> }
> ```

สำหรับงานทั่วไป (Dam Break, Tank Sloshing):

| Parameter | Value | Note |
| :--- | :--- | :--- |
| `adjustTimeStep` | `yes` | ต้องเปิดเสมอ |
| `maxCo` | `0.8 - 1.0` | เพื่อความปลอดภัยของ Momentum |
| `maxAlphaCo` | `0.5 - 0.8` | เพื่อความคมของ Interface |
| `nAlphaSubCycles` | `2 - 3` | ช่วยเพิ่มความเสถียรและผิวคมขึ้น |
| `deltaT` (initial) | `1e-6` | เริ่มต้นเล็กๆ ไว้ก่อน แล้วให้โปรแกรมปรับเพิ่มเอง |

---

## 🧠 Concept Check: ทดสอบความเข้าใจ

1.  **ถ้าเราลดขนาด Mesh ให้ละเอียดขึ้น 2 เท่า ( $\Delta x$ ลดลงครึ่งหนึ่ง) โดยความเร็วเท่าเดิม เราต้องทำอย่างไรกับ $\Delta t$ เพื่อรักษา $Co$ ให้เท่าเดิม?**
    <details>
    <summary>เฉลย</summary>
    ตามสูตร $Co = U \Delta t / \Delta x$ ถ้า $\Delta x$ ลดลง 2 เท่า ตัวหารลดลง ค่า $Co$ จะเพิ่ม 2 เท่า ดังนั้นเราต้อง **ลด $\Delta t$ ลง 2 เท่า** ด้วยเช่นกัน (Simulation จะช้าลง 2 เท่า!)
    </details>

2.  **ทำไมช่วงแรกของ Dam Break ถึงมักจะ Crash?**
    <details>
    <summary>เฉลย</summary>
    เพราะน้ำเปลี่ยนจาก "นิ่งสนิท" เป็น "เคลื่อนที่เร็วมาก" ในพริบตา ถ้า `deltaT` เริ่มต้นตั้งไว้ใหญ่เกินไป Adaptive Method จะปรับตัวไม่ทัน ทำให้ $Co$ พุ่งเกิน 1 ในก้าวแรกและ Diverge ทันที **วิธีแก้:** เริ่มด้วย `deltaT` เล็กมากๆ
    </details>

3.  **ค่า `maxAlphaCo` คืออะไรและควรตั้งค่าอย่างไรเมื่อเทียบกับ `maxCo`?**
    <details>
    <summary>เฉลย</summary>
    `maxAlphaCo` คือ Courant Number ที่คำนวณเฉพาะบริเวณที่มีการเปลี่ยนเฟส (Interface) เพื่อควบคุมความเสถียรของการติดตามผิว ควรตั้งค่าให้ **เท่ากับหรือต่ำกว่า** `maxCo` (เช่น 0.5-0.8) เพื่อให้แน่ใจว่า Interface จะไม่เคลื่อนที่ข้ามเซลล์เร็วเกินไปจน MULES จับไม่ทัน
    </details>

---

## 📖 เอกสารที่เกี่ยวข้อง

*   **บทก่อนหน้า**: [03_Setting_Up_InterFoam.md](03_Setting_Up_InterFoam.md)
*   **บทถัดไป**: [../03_EULER_EULER_METHOD/00_Overview.md](../03_EULER_EULER_METHOD/00_Overview.md)