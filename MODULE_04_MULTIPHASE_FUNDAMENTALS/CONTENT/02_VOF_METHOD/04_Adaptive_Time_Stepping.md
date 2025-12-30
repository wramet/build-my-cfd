# การจัดการเวลาแบบอัตโนมัติ (Adaptive Time Stepping)

> [!TIP] **ทำไม Adaptive Time Stepping ถึงสำคัญ?**
> ในการจำลอง VOF ที่มีการเปลี่ยนแปลงของความเร็วของของไหลอย่างมหาศาล (เช่น เขื่อนแตก คลื่นกระแทก) การกำหนด Time Step คงที่เป็นไปไม่ได้ เพราะ:
> - **ช่วงแรก:** น้ำนิ่ง ($\mathbf{U} \approx 0$) → ใช้ Time Step ใหญ่ได้ (ประหยัดเวลา)
> - **ช่วงกลาง:** น้ำทะลัก ($\mathbf{U}$ สูงมาก) → ต้องลด Time Step ทันที (ป้องกัน Diverge)
> - **ช่วงท้าย:** น้ำเริ่มนิ่ง → ขยาย Time Step กลับมาได้ (ประหยัดเวลาอีกครั้ง)
>
> **Adaptive Time Stepping** ใน OpenFOAM จะคำนวณและปรับ $\Delta t$ อัตโนมัติตามค่า Courant Number เพื่อให้ได้ความสมดุลระหว่าง **ความเสถียร** (Stability) และ **ความเร็วในการคำนวณ** (Computational Efficiency)

---

## What You Will Learn

ในบทนี้คุณจะเรียนรู้:

- **ความเข้าใจ Courant Number (Co):** แนวคิดพื้นฐานที่ใช้ควบคุมความเสถียรของการคำนวณ
- **การตั้งค่า Adaptive Time Stepping:** วิธีปรับแต่งพารามิเตอร์ใน `controlDict` และ `fvSolution`
- **การแยกควบคุม maxCo และ maxAlphaCo:** ความแตกต่างระหว่างการคุม Momentum และ Interface
- **การใช้ Sub-cycling ร่วมกับ Adaptive Time Stepping:** เทคนิคเพิ่มประสิทธิภาพการคำนวณ
- **การแก้ปัญหาที่พบบ่อย:** Troubleshooting เมื่อ Time Step ทำตัวผิดปกติ

---

## Prerequisites

ก่อนดำเนินการต่อ คุณควรมีความเข้าใจพื้นฐานเกี่ยวกับ:

- **การตั้งค่า Simulation พื้นฐาน:** โครงสร้างไฟล์ OpenFOAM (controlDict, fvSolution, fvSchemes)
- **แนวคิด Mesh และ Cell:** ขนาดเซลล์ ($\Delta x$) และความสัมพันธ์กับ Time Step
- **พื้นฐาน VOF Method:** ความเข้าใจเกี่ยวกับ $\alpha$ field และ Interface (ดูในบทที่แล้ว)
- **Solver interFoam:** ความเข้าใจโครงสร้างการทำงานของ interFoam

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

### การทำงานของ Adaptive Time Stepping

เมื่อ `adjustTimeStep yes;` ถูกตั้งค่า OpenFOAM จะทำงานดังนี้ในทุก Time Step:

1. **คำนวณ $Co$ จาก Velocity Field ปัจจุบัน**
2. **ปรับ $\Delta t$ ใหม่** ตามสูตร: $\Delta t_{new} = \frac{maxCo \cdot \Delta x}{|\mathbf{U}|}$
3. **ตรวจสอบ Constraints:** ตรวจสอบว่า $\Delta t_{new} < maxDeltaT$

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

เพื่อเปิดใช้งานระบบอัตโนมัติ ให้ตั้งค่าดังนี้ใน `system/controlDict`:

```cpp
application     interFoam;
startFrom       latestTime;

adjustTimeStep  yes;    // เปิดใช้งาน Adaptive Time Stepping

maxCo           1.0;    // เป้าหมาย Courant Number สูงสุดสำหรับการไหล (U)
maxAlphaCo      1.0;    // เป้าหมาย Courant Number สูงสุดสำหรับ Interface (สำคัญ!)

maxDeltaT       1.0;    // ห้ามเกินค่านี้ (กันเหนียว)

deltaT          1e-6;   // เริ่มต้นเล็กๆ แล้วให้โปรแกรมปรับเพิ่มเอง
```

### `maxCo` vs `maxAlphaCo` ต่างกันอย่างไร?

| พารามิเตอร์ | คำนวณจาก | ใช้ควบคุม | ค่าแนะนำ |
|:---|:---|:---|:---|
| **`maxCo`** | ความเร็วเฉลี่ยของของไหล ($\mathbf{U}$) ทั่วโดเมน | ความเสถียรของสมการโมเมนตัม | 0.8 - 1.0 |
| **`maxAlphaCo`** | เฉพาะบริเวณที่มี **Interface** ($0 < \alpha < 1$) | ความคมชัดของ Interface (MULES) | 0.5 - 0.8 |

**หมายเหตุสำคัญ:**
- **`maxAlphaCo`** สำหรับ VOF คือค่าที่สำคัญที่สุด!
- ถ้า Interface วิ่งเร็วเกินกว่าที่ MULES จะจับทัน ผิวจะเบลอหรือเกิดฟองอากาศปลอม
- **แนะนำ:** ตั้ง `maxAlphaCo` ให้เท่ากับหรือต่ำกว่า `maxCo` เสมอ (เช่น 0.5 - 0.8 เพื่อความชัวร์)

---

## 3. Sub-cycling กับ Adaptive Time Stepping

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

**การตั้งค่าใน `system/fvSolution`:**

```cpp
solvers
{
    "alpha.*"
    {
        nAlphaSubCycles 2;    // จำนวน Sub-cycles สำหรับ Alpha
        // ...
    }
}
```

### กลไกการทำงานของ Sub-cycling

การใช้ **Sub-cycling** (`nAlphaSubCycles`) ช่วยให้เรา "โกง" ได้นิดหน่อย:

- ถ้า `nAlphaSubCycles 3` เราอาจปล่อยให้ $Co$ ของ Momentum ขึ้นไปถึง 1.5 - 2.0 ได้ (ถ้าจำเป็น)
- เพราะสมการ Alpha จะถูกแก้ด้วย $\Delta t_{sub} = \Delta t / 3$
- ทำให้ $Co_{\alpha}$ ที่แท้จริงเหลือแค่ $2.0 / 3 = 0.66$ (ซึ่งปลอดภัย!)

> [!TIP] **เมื่อไหร่ควรใช้ Sub-cycling?**
> - **กรณีที่ 1:** Interface ซับซ้อนหรือเคลื่อนที่เร็ว (เช่น คลื่นกระแทก)
> - **กรณีที่ 2:** Mesh ละเอียดมากแต่อยากใช้ Time Step ใหญ่
> - **กรณีที่ 3:** เกิดปัญหา Interface เบลอแม้ `maxAlphaCo` ต่ำอยู่แล้ว
>
> **ข้อควรระวัง:** Sub-cycling จะเพิ่มเวลาคำนวณต่อ Time Step แต่อาจช่วยลดจำนวน Time Step ทั้งหมดได้

> [!NOTE] **📚 อ่านเพิ่มเติมเกี่ยวกับ Sub-cycling**
> สำหรับรายละเอียดเพิ่มเติมเกี่ยวกับ Sub-cycling และผลกระทบต่อ Interface Compression แนะนำให้อ่าน **[Section 4: Interface Compression](02_Interface_Compression.md#4-sub-cycling)** ซึ่งครอบคลุม:
> - ความสัมพันธ์ระหว่าง `nAlphaSubCycles` และ `nAlphaCorr`
> - ผลกระทบต่อความแม่นยำของ Interface
> - Trade-off ระหว่างความเสถียรและเวลาคำนวณ

---

## 4. การแก้ปัญหาที่พบบ่อย (Troubleshooting)

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

### Problem 1: Time step ลดลงเรื่อยๆ จนเหลือ $10^{-20}$

**สาเหตุ:** มักเกิดจาก "Bad Mesh" หรือความเร็วที่ระเบิดผิดปกติ (Spurious Velocity)

**วิธีแก้:**

1. **Check Mesh:** รัน `checkMesh` เพื่อตรวจสอบค่า Skewness หรือ Non-orthogonality
2. **Limit Velocity:** ใช้ `fvOptions` เพื่อจำกัดความเร็วสูงสุด (`velocityDamping`) ไม่ให้เกินจริง
3. **Relaxation:** ปรับลด Relaxation factor ใน `fvSolution`

```cpp
// ตัวอย่างการใช้ fvOptions จำกัดความเร็ว
velocityDamping
{
    type            scalarLimit;
    active          yes;
    scalarLimitCoeffs
    {
        max           10.0;    // ความเร็วสูงสุด (m/s)
    }
}
```

### Problem 2: Simulation ช้ามาก แต่ $Co$ ยังต่ำอยู่

**สาเหตุ:** อาจตั้ง `maxCo` ต่ำเกินความจำเป็น (เช่น 0.1)

**วิธีแก้:** ลองขยับ `maxCo` ขึ้นมาเป็น 0.8 - 1.0 (interFoam สมัยใหม่ทนทานพอสมควร)

### Problem 3: Simulation Diverge ในช่วงแรกของ Dam Break

**สาเหตุ:** น้ำเปลี่ยนจาก "นิ่งสนิท" เป็น "เคลื่อนที่เร็วมาก" ในพริบตา ถ้า `deltaT` เริ่มต้นตั้งไว้ใหญ่เกินไป Adaptive Method จะปรับตัวไม่ทัน

**วิธีแก้:**
- เริ่มด้วย `deltaT` เล็กมากๆ (เช่น `1e-6`)
- ตั้ง `maxDeltaT` ไว้เป็น Safety limit

### Summary Table: การวินิจฉัยปัญหา

| อาการ | สาเหตุที่เป็นไปได้ | วิธีแก้ |
|:---|:---|:---|
| Time step ลดเรื่อยๆ | Bad Mesh / Spurious Velocity | checkMesh, velocityDamping |
| Simulation ช้ามาก | `maxCo` ต่ำเกินไป | เพิ่ม `maxCo` เป็น 0.8-1.0 |
| Diverge ช่วงแรก | `deltaT` เริ่มต้นใหญ่เกินไป | เริ่มด้วย `1e-6` |
| Interface เบลอ | `maxAlphaCo` สูงเกินไป | ลด `maxAlphaCo` หรือเพิ่ม `nAlphaSubCycles` |

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

สำหรับงานทั่วไป (Dam Break, Tank Sloshing):

### การตั้งค่าใน `controlDict`

```cpp
application     interFoam;
startFrom       latestTime;

adjustTimeStep  yes;
maxCo           0.8;
maxAlphaCo      0.5;
maxDeltaT       1.0;

deltaT          1e-6;  // เริ่มต้นเล็กๆ
```

### การตั้งค่าใน `fvSolution`

```cpp
solvers
{
    "alpha.*"
    {
        nAlphaSubCycles 2;
        // ...
    }
}
```

### ตารางสรุปพารามิเตอร์

| Parameter | Value | Note |
|:---|:---|:---|
| `adjustTimeStep` | `yes` | ต้องเปิดเสมอ |
| `maxCo` | `0.8 - 1.0` | เพื่อความปลอดภัยของ Momentum |
| `maxAlphaCo` | `0.5 - 0.8` | เพื่อความคมของ Interface |
| `nAlphaSubCycles` | `2 - 3` | ช่วยเพิ่มความเสถียรและผิวคมขึ้น |
| `deltaT` (initial) | `1e-6` | เริ่มต้นเล็กๆ ไว้ก่อน แล้วให้โปรแกรมปรับเพิ่มเอง |

---

## 🧠 Concept Check: ทดสอบความเข้าใจ

<details>
<summary><b>Question 1: Mesh ละเอียดขึ้น 2 เท่า ต้องทำอย่างไร?</b></summary>

ถ้าเราลดขนาด Mesh ให้ละเอียดขึ้น 2 เท่า ( $\Delta x$ ลดลงครึ่งหนึ่ง) โดยความเร็วเท่าเดิม เราต้องทำอย่างไรกับ $\Delta t$ เพื่อรักษา $Co$ ให้เท่าเดิม?

<details>
<summary>เฉลย</summary>

ตามสูตร $Co = U \Delta t / \Delta x$ ถ้า $\Delta x$ ลดลง 2 เท่า ตัวหารลดลง ค่า $Co$ จะเพิ่ม 2 เท่า ดังนั้นเราต้อง **ลด $\Delta t$ ลง 2 เท่า** ด้วยเช่นกัน (Simulation จะช้าลง 2 เท่า!)

</details>
</details>

---

<details>
<summary><b>Question 2: ทำไมช่วงแรกของ Dam Break ถึงมักจะ Crash?</b></summary>

<details>
<summary>เฉลย</summary>

เพราะน้ำเปลี่ยนจาก "นิ่งสนิท" เป็น "เคลื่อนที่เร็วมาก" ในพริบตา ถ้า `deltaT` เริ่มต้นตั้งไว้ใหญ่เกินไป Adaptive Method จะปรับตัวไม่ทัน ทำให้ $Co$ พุ่งเกิน 1 ในก้าวแรกและ Diverge ทันที

**วิธีแก้:** เริ่มด้วย `deltaT` เล็กมากๆ (เช่น `1e-6`)

</details>
</details>

---

<details>
<summary><b>Question 3: maxAlphaCo vs maxCo?</b></summary>

ค่า `maxAlphaCo` คืออะไรและควรตั้งค่าอย่างไรเมื่อเทียบกับ `maxCo`?

<details>
<summary>เฉลย</summary>

`maxAlphaCo` คือ Courant Number ที่คำนวณเฉพาะบริเวณที่มีการเปลี่ยนเฟส (Interface) เพื่อควบคุมความเสถียรของการติดตามผิว

**ควรตั้งค่า:** ให้ **เท่ากับหรือต่ำกว่า** `maxCo` (เช่น 0.5-0.8) เพื่อให้แน่ใจว่า Interface จะไม่เคลื่อนที่ข้ามเซลล์เร็วเกินไปจน MULES จับไม่ทัน

</details>
</details>

---

## How to Apply (Key Takeaways)

### สิ่งสำคัญที่ควรนำไปใช้

1. **เปิด Adaptive Time Stepping เสมอ:** ตั้ง `adjustTimeStep yes;` ใน `controlDict`
2. **แยกคุม maxCo และ maxAlphaCo:** ให้ `maxAlphaCo <= maxCo` เพื่อ Interface ที่คมชัด
3. **เริ่มต้นด้วย deltaT เล็กๆ:** ใช้ `1e-6` แล้วปล่อยให้ Adaptive ทำงาน
4. **ใช้ Sub-cycling เมื่อจำเป็น:** เพิ่ม `nAlphaSubCycles` ถ้า Interface ยังเบลอแม้คุม maxAlphaCo แล้ว
5. **ตรวจสอบ Mesh quality:** Bad mesh ทำให้ Time step ลดลงเรื่อยๆ ใช้ `checkMesh` ช่วยวินิจฉัย

### การประยุกต์ใช้กับงานของคุณ

- **Dam Break:** เริ่มด้วย `deltaT 1e-6`, `maxCo 0.8`, `maxAlphaCo 0.5`, `nAlphaSubCycles 2`
- **Tank Sloshing:** เพิ่ม `maxCo` ได้ถึง 1.0 ถ้า Mesh ดี, ลด `maxAlphaCo` เหลือ 0.3-0.5
- **คลื่นกระแทก:** ใช้ `nAlphaSubCycles 3` เพื่อความเสถียรของ Interface

---

## 📖 เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [03_Setting_Up_InterFoam.md](03_Setting_Up_InterFoam.md)
- **บทถัดไป:** [../03_EULER_EULER_METHOD/00_Overview.md](../03_EULER_EULER_METHOD/00_Overview.md)
- **อ่านเพิ่มเติมเรื่อง Sub-cycling:** [02_Interface_Compression.md](02_Interface_Compression.md#4-sub-cycling)