# การบีบอัดผิวหน้าและ MULES (Interface Compression & MULES)

## What You Will Learn
- วิธีการทำงานของ Interface Compression Term ที่แก้ปัญหา Numerical Diffusion
- การเลือกและปรับค่า `cAlpha` ที่เหมาะสมกับงานของคุณ
- กลไกการทำงานของ MULES และ FCT Algorithm ที่รักษา Boundedness และ Mass Conservation
- เทคนิค Sub-cycling และการตั้งค่าขั้นสูงเพื่อความเสถียร
- ความแตกต่างระหว่าง Explicit MULES, Semi-Implicit MULES และ isoAdvector

## Prerequisites
- ความเข้าใจพื้นฐานเรื่อง Volume of Fluid (VOF) Method และสมการ Transport
- ความคุ้นเคยกับไฟล์การตั้งค่า OpenFOAM: `system/fvSolution`, `system/fvSchemes`, `system/controlDict`
- ความเข้าใจเรื่อง Courant Number และเสถียรภาพของการคำนวณ CFD

---

> [!TIP] **Why This Matters**
> การบีบอัดผิวหน้า (Interface Compression) และ MULES คือหัวใจสำคัญที่ทำให้การจำลองกระแส 2 เฟสด้วย VOF ใน OpenFOAM ประสบความสำเร็จได้จริง หากไม่มีเทคนิคเหล่านี้ ผิวน้ำจะเบลอและกระจายตัวไปทั้้งโดเมน (Numerical Diffusion) ทำให้ผลลัพธ์ไม่น่าเชื่อถือ การเข้าใจ `cAlpha`, `nAlphaCorr`, และ `nAlphaSubCycles` จะช่วยให้คุณควบคุมความคมของผิวน้ำและเสถียรภาพของการคำนวณได้อย่างมืออาชีพ

---

## 1. ปัญหา Numerical Diffusion และวิธีแก้ของ OpenFOAM

ปัญหาโลกแตกของวิธีการ **Volume of Fluid (VOF)** แบบดั้งเดิมคือ "ผิวเบลอ" (Numerical Diffusion) จากการแก้สมการ Transport ด้วยรูปแบบ Discretization ทั่วไป

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **การกำหนด Discretization Scheme** ในไฟล์ `system/fvSchemes`:
> - **divSchemes**: การ discretize เทอม advection $\nabla \cdot (\mathbf{U} \alpha)$ ใช้ `Gauss vanLeer` หรือ `Gauss linearDiv`
> - **การเพิ่มเทอม Compression**: เทอม $\nabla \cdot (\mathbf{U}_r \alpha (1-\alpha))$ ถูกเพิ่มโดยอัตโนมัติใน solver ผ่านคลาส `MULES`
> - **Field**: ค่า $\alpha$ ถูกเก็บในไฟล์ `0/alpha.water` (หรือ phase อื่นๆ)
>
> ที่มาของสมการนี้อยู่ใน source code ที่ `src/finiteVolume/interpolation/interpolationSchemes/` และ `src/transportModels/geometricVoF/`

แทนที่จะใช้เทคนิคทางเรขาคณิตที่ซับซ้อน (อย่าง PLIC - Piecewise Linear Interface Calculation) OpenFOAM เลือกที่จะ **แก้สมการคณิตศาสตร์เพิ่มอีกเทอม**:

$$ \frac{\partial \alpha}{\partial t} + \nabla \cdot (\mathbf{U} \alpha) + \underbrace{\nabla \cdot (\mathbf{U}_r \alpha (1-\alpha))}_{\text{The Magic Term}} = 0 $$

### 1.1 เจาะลึกกลไกของ "เทอมวิเศษ"

**1. Active only at Interface:** สังเกตเทอม $\alpha(1-\alpha)$
- ในน้ำ ($\alpha=1$) $\rightarrow 1(0) = 0$
- ในอากาศ ($\alpha=0$) $\rightarrow 0(1) = 0$
- **ที่รอยต่อ ($0 < \alpha < 1$)** $\rightarrow \text{มีค่า} \neq 0$
- *ผลลัพธ์:* เทอมนี้จะทำงานเฉพาะจุดที่เป็น Interface เท่านั้น ไม่กระทบส่วนอื่น

**2. Compression Velocity ($\mathbf{U}_r$):**
เป็นความเร็วเสมือนที่สร้างขึ้นมาเพื่อ "กด" ไหลเข้าหากันในทิศทางตั้งฉากกับผิว:
$$ \mathbf{U}_r = \mathbf{n}_{\alpha} \cdot \min(c_{\alpha}|\phi|, |\phi_{max}|) $$
โดยที่ $\mathbf{n}_{\alpha} = \frac{\nabla \alpha}{|\nabla \alpha|}$ คือเวกเตอร์ตั้งฉากผิวหน้า

**3. Physical Meaning:**
มันคือการบอกโปรแกรมว่า *"เฮ้ ตรงไหนที่เป็นรอยต่อ ให้สร้างกระแสไหลย้อนกลับเข้าหากันหน่อยนะ เพื่อต้านทานการแพร่ (Diffusion)"*

---

## 2. พารามิเตอร์ `cAlpha` (The Compression Factor)

> [!NOTE] **📂 OpenFOAM Context**
> พารามิเตอร์ `cAlpha` ถูกกำหนดในไฟล์ `system/fvSolution`:
> - **Location**: อยู่ภายใต้ `solvers` → `"alpha.water.*"` → `cAlpha`
> - **ค่าที่ใช้**: `cAlpha 1;` (ค่ามาตรฐาน), `cAlpha 0;` (ปิดการบีบอัด), `cAlpha 2;` (บีบแรง)
> - **ผลต่อ Solver**: ค่านี้ถูกส่งไปยังคลาส `MULES` ใน source code เพื่อคำนวณ $\mathbf{U}_r = c_{\alpha} \cdot \mathbf{U}_{interface}$
>
> ดูตัวอย่างการตั้งค่าได้ที่ `etc/tutorialDict` หรือใน `tutorials/multiphase/interFoam/`

ในไฟล์ `system/fvSolution` คุณสามารถคุมระดับความแรงของการบีบได้ผ่าน `cAlpha`:

<!-- IMAGE: IMG_04_002 -->
<!-- 
Purpose: เพื่อแสดงผลของค่า `cAlpha` ในไฟล์ `fvSolution` ว่าทำหน้าที่ "บีบ" Interface ให้คมขึ้นได้อย่างไร และถ้าบีบมากไปจะเกิดอะไรขึ้น. ภาพนี้ต้องช่วยผู้เรียนจูนค่า `cAlpha` ได้อย่างมั่นใจ
Prompt: "Comparative visualization of VOF Interface Sharpness (3 Panels). The scene is a water droplet falling in air. **Panel 1 (cAlpha = 0):** The droplet edge is extremely blurry/smeared across many cells (Numerical Diffusion). Color fades from blue to white over a wide distance. **Panel 2 (cAlpha = 1 - Standard):** The droplet edge is sharp and crisp, confined to 1-2 cells. Perfect balance. **Panel 3 (cAlpha > 2 - Aggressive):** The interface is razor-sharp (1 cell) but shows unphysical 'wiggles' or spiky artifacts on the surface (Over-compression instability). STYLE: High-end CFD post-processing simulation render, using a 'cool-warm' or 'blue-white' colormap to show $\alpha$ concentration."
-->
![[IMG_04_002.jpg]]

### 2.1 ผลของค่า cAlpha ที่ต่างกัน

| ค่า `cAlpha` | พฤติกรรม (Behavior) | คำแนะนำ (Recommendation) |
| :---: | :--- | :--- |
| **0** | ปิดการบีบอัด | ไม่แนะนำ ผิวจะเบลอเละในไม่กี่ steps ยกเว้นคุณต้องการจำลองการกระจายตัวของสารเคมี (Scalar transport) |
| **1** | **Conservative Compression** | **ค่าแนะนำมาตรฐาน** บีบความเร็วเท่ากับความเร็วการไหลจริง ($\mathbf{U}_r \approx \mathbf{U}$) ให้ผิวคมประมาณ 2-3 Cells และรักษา Boundedness ได้ดี |
| **> 1** | Over-Compression | บีบแรงกว่าปกติ ผิวจะคมกริบ (1-2 Cells) แต่อาจเกิด **Wiggles** (รอยหยัก) หรือฟองอากาศปลอมๆ ได้ เหมาะกับงาน Static หรือ Quasi-static |

> [!WARNING] **อย่าปรับเพลิน!**
> ค่า `cAlpha` ที่สูงเกินไป (> 1.5) อาจทำให้เกิดแรง Parasitic Currents ที่รุนแรง และทำให้ Solver ลู่เข้ายากขึ้น

---

## 3. MULES Algorithm (The Guardian)

> [!NOTE] **📂 OpenFOAM Context**
> อัลกอริทึม MULES ถูก implement ใน OpenFOAM source code:
> - **Source Code**: อยู่ใน `src/finiteVolume/fvMatrices/solvers/MULES/`
> - **การถูกเรียกใช้**: Solver อย่าง `interFoam` เรียก `MULES::explicitSolve()` ในไฟล์ `.H` ของ solver
> - **การตั้งค่า**: ผ่าน `MULESCorr`, `nLimiterIter` ใน `system/fvSolution`
> - **Output**: ผลลัพธ์จะถูกเขียนลง `0/alpha.water` ทุก time step โดยรักษาค่าให้อยู่ใน [0,1] เสมอ
>
> MULES ทำหน้าที่เป็น "Flux Limiter" ระดับโค้ด ไม่ใช่ user input แต่สามารถปรับแต่งพฤติกรรมผ่าน parameters ใน `fvSolution` ได้

**MULES** ย่อมาจาก **M**ultidimensional **U**niversal **L**imiter for **E**xplicit **S**olution.

หน้าที่ของมันคือเป็น "ผู้คุมกฎ" (Limiter) เพื่อรับประกันว่า:
1. **Boundedness:** $0 \le \alpha \le 1$ เสมอ (ห้ามมีค่าน้ำ -0.1 หรือ 1.2 เด็ดขาด)
2. **Mass Conservation:** มวลรวมของน้ำในระบบต้องเท่าเดิมเป๊ะๆ ไม่ว่าจะผ่านไปกี่ล้าน Time steps

### 3.1 กลไกการทำงาน: FCT (Flux Corrected Transport)

MULES ทำงานคล้ายกับเทคนิค FCT ซึ่งมีขั้นตอนดังนี้:

> [!INFO] **FCT Algorithm Step-by-Step**
> **Step 1: Calculate Low-Order Flux**  
> คำนวณ Flux แบบ Upwind (เสถียรแต่เบลอ/Diffusive)
> 
> **Step 2: Calculate High-Order Flux**  
> คำนวณ Flux แบบ High-order scheme เช่น vanLeer, ULTRA (แม่นยำแต่อาจแกว่ง/Oscillatory)
> 
> **Step 3: Compute Anti-Diffusive Flux**  
> $\phi_{AD} = \phi_{High} - \phi_{Low}$ (ส่วนที่ทำให้คมขึ้น)
> 
> **Step 4: Apply Limiter**  
> คำนวณค่า Limiter coefficient $\lambda \in [0,1]$ สำหรับทุก Face เพื่อรับประกันว่าค่า $\alpha$ ใหม่จะอยู่ใน [0,1]
> 
> **Step 5: Update Solution**  
> $\alpha^{n+1} = \alpha^n + \Delta t \left[ \nabla \cdot \phi_{Low} + \lambda \nabla \cdot \phi_{AD} \right]$

```mermaid
flowchart TD
    Start[Start Time Step] --> Low[Calculate Low-Order Flux<br/>(Upwind - Stable but Diffusive)]
    Low --> High[Calculate High-Order Flux<br/>(vanLeer - Sharp but Oscillatory)]
    High --> Anti[Compute Anti-Diffusive Flux<br/>Φ_AD = Φ_High - Φ_Low]
    Anti --> Limit{Apply Limiter λ<br/>Check Bounds [0,1]}
    Limit -- λ computed --> Combine[Combine: Φ = Φ_Low + λ·Φ_AD]
    Combine --> MassCheck{Global Mass<br/>Conservation Check}
    MassCheck -- OK --> Update[Update α Field]
    MassCheck -- Violation --> Iterate[Increase nLimiterIter<br/>Recompute Limiter]
    Iterate --> Limit
    Update --> End[End Time Step]
```

---

## 4. การตั้งค่า VOF ขั้นสูง (Advanced Configuration)

> [!NOTE] **📂 OpenFOAM Context**
> การตั้งค่าขั้นสูงเหล่านี้อยู่ในไฟล์ `system/fvSolution`:
> - **Section**: `solvers { "alpha.water.*" { ... } }`
> - **Keywords สำคัญ**: `nAlphaCorr`, `nAlphaSubCycles`, `MULESCorr`, `nLimiterIter`
> - **Linear Solver Settings**: `solver`, `smoother`, `tolerance`, `relTol`
> - **ผลกระทบ**: ค่าเหล่านี้ควบคุมความแม่นยำและเสถียรภาพของการแก้สมการ VOF
>
> การปรับค่าเหล่านี้ต้องแลกกับ **เวลาคำนวณ** ยิ่งแม่นยำยิ่งคำนวณช้า ดูตัวอย่างเพิ่มเติมใน `tutorials/multiphase/interFoam/laminar/damBreak/`

ตัวอย่างการตั้งค่าใน `system/fvSolution` สำหรับงานที่ต้องการความแม่นยำสูง:

```cpp
solvers
{
    "alpha.water.*"
    {
        // 1. Solver Selection
        nAlphaCorr      2;          // แก้สมการ Alpha 2 รอบต่อ Time step (เพิ่มความแม่น)
        nAlphaSubCycles 3;          // ซอย Time step ย่อยสำหรับ Alpha เป็น 3 ส่วน (เสถียรมาก)
        cAlpha          1;          // แรงบีบมาตรฐาน
        
        // 2. MULES Settings
        MULESCorr       yes;        // ใช้ Corrector loop
        nLimiterIter    5;          // วนลูปหาค่า Limiter 5 ครั้งเพื่อให้มวลหายเท่ากับ 0
        
        // 3. Linear Solver
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-9;       // ต้องการความแม่นยำสูง
        relTol          0;
    }
}
```

### 4.1 เคล็ดลับ Sub-cycling (`nAlphaSubCycles`)

> [!NOTE] **📂 OpenFOAM Context**
> เทคนิค Sub-cycling ถูกกำหนดใน `system/fvSolution`:
> - **Parameter**: `nAlphaSubCycles 3;` (ตัวอย่าง)
> - **ความสัมพันธ์กับ Time Step**: เทคนิคนี้ทำให้สามารถใช้ `deltaT` ที่ใหญ่ขึ้นใน `system/controlDict` โดยที่ $\alpha$ ยังคงเสถียร
> - **Courant Number**: อนุญาตให้ $Co_{\alpha} > 0.5$ ได้ แต่ต้องมี Sub-cycles เพียงพอ
> - **การ Monitor**: ใช้ `functionObjects` ใน `controlDict` เพื่อ track Courant number ของแต่ละ phase

เนื่องจากสมการ $\alpha$ อ่อนไหวต่อ Courant Number มากกว่าสมการโมเมนตัม เราจึงใช้เทคนิค **Sub-cycling**:
- สมมติ Time step หลัก ($\Delta t$) = 0.01 วินาที
- ถ้าตั้ง `nAlphaSubCycles 4` โปรแกรมจะแก้ $\alpha$ ด้วย $\Delta t_{\alpha} = 0.0025$ วินาที จำนวน 4 ครั้ง
- จากนั้นค่อยเอาค่าเฉลี่ยไปแก้ Momentum
- **ข้อดี:** ทำให้เราใช้ $\Delta t$ รวมใหญ่ขึ้นได้ โดยที่ Alpha ไม่ระเบิด!

### 4.2 Parameters Quick Reference

| Parameter | Location | Typical Range | Use Case |
|:---|:---|:---:|:---|
| **cAlpha** | `fvSolution` → `solvers` | 0-2 | 1 = Standard, >1 = Sharper (risky) |
| **nAlphaCorr** | `fvSolution` → `solvers` | 1-3 | Higher = More accurate, slower |
| **nAlphaSubCycles** | `fvSolution` → `solvers` | 1-5 | Higher = Allows larger $\Delta t$ |
| **MULESCorr** | `fvSolution` → `solvers` | yes/no | yes = Better mass conservation |
| **nLimiterIter** | `fvSolution` → `solvers` | 1-10 | Higher = Stricter boundedness |
| **maxCo** | `controlDict` | 0.1-1.0 | Keep < 0.5 for explicit MULES |

---

## 5. ตระกูลของ MULES และ Solver Alternatives

> [!NOTE] **📂 OpenFOAM Context**
> การเลือกใช้ VOF solver ที่ต่างกันขึ้นอยู่กับ:
> - **interFoam**: ใช้ Explicit MULES แบบดั้งเดิม (Standard VOF)
> - **interIsoFoam**: ใช้ isoAdvector (Geometric reconstruction) ไม่ต้องตั้ง `cAlpha`
> - **interDyMFoam**: สำหรับ mesh that moves/deforms
> - **multiphaseInterFoam**: สำหรับหลาย phase (> 2 phases)
>
> ดูตัวอย่างการใช้งาน solver ต่างๆ ได้ใน `tutorials/multiphase/`

OpenFOAM มีวิวัฒนาการ MULES หลายเวอร์ชัน:

1. **Explicit MULES (Original):** แม่นยำที่สุด แต่จำกัดที่ $Co_{\alpha} < 0.5$ เพื่อความเสถียร
2. **Semi-Implicit MULES (Newer):** ผ่อนปรนเงื่อนไข Courant number ได้บ้าง ($Co \approx 1-2$) แต่ความคมอาจลดลงเล็กน้อย

---

> [!TIP] **🚀 Advanced Topics: isoAdvector**
> **interIsoFoam** ใช้เทคนิค **isoAdvector** ซึ่งเป็น Game Changer! ไม่ใช้ MULES แบบบีบอัด แต่ใช้เทคนิค Geometric Reconstruction จริงๆ (ตัดระนาบในเซลล์) ทำให้ผิวคมกริบภายใน 1 Cell โดยไม่ต้องปรับ `cAlpha`
> 
> **ข้อดี:**
> - ผิวคมกริบมาก (1 cell) โดยไม่เกิด Wiggles
> - ไม่ต้องจูน `cAlpha` 
> - เสถียรกับ Courant number สูงกว่า
> 
> **ข้อเสีย:**
> - คำนวณช้ากว่า MULES ปกติ
> - ซับซ้อนกว่าในการ Debug
> 
> *แนะนำให้ลองใช้ `interIsoFoam` หากต้องการความแม่นยำระดับงานวิจัย*

---

## 6. Common Pitfalls & Troubleshooting

> [!WARNING] **⚠️ ปัญหาที่พบบ่อย**
> 
> **1. ผิวน้ำเบลอ (Blurry Interface)**
> - **สาเหตุ:** `cAlpha = 0` หรือค่า Courant number สูงเกินไป
> - **วิธีแก้:** เพิ่ม `cAlpha` เป็น 1-1.5 หรือลด `maxCo` ใน controlDict
> 
> **2. เกิดฟองอากาศปลอม (Spurious Bubbles)**
> - **สาเหตุ:** `cAlpha` สูงเกินไป (> 2) หรือ Mesh ไม่สม่ำเสมอ
> - **วิธีแก้:** ลด `cAlpha` หรือเปลี่ยนไปใช้ `interIsoFoam`
> 
> **3. ค่า α หลุดจาก [0,1] (Unbounded Solution)**
> - **สาเหตุ:** Courant number สูงเกินไป หรือไม่ได้ใช้ MULES
> - **วิธีแก้:** ลด `deltaT` หรือเพิ่ม `nAlphaSubCycles`
> 
> **4. มวลน้ำไม่คงที่ (Mass Loss/Gain)**
> - **สาเหตุ:** `nLimiterIter` ต่ำเกินไป หรือไม่ได้เปิด `MULESCorr`
> - **วิธีแก้:** เพิ่ม `nLimiterIter` เป็น 5-10 และเปิด `MULESCorr yes`
> 
> **5. Solver ลู่เข้ายาก (Divergence)**
> - **สาเหตุ:** ผิดพลานามในไฟล์ `0/alpha.water` เริ่มต้น หรือ `cAlpha` สูงเกินไป
> - **วิธีแก้:** ตรวจสอบค่าเริ่มต้นให้ถูกต้อง และเริ่มจาก `cAlpha = 1`

---

## 🧠 Concept Check: ทดสอบความเข้าใจ

<details>
<summary><b>Question 1: ทำไมเทอมบีบอัด $\nabla \cdot (\mathbf{U}_r \alpha (1-\alpha))$ ถึงไม่มีผลในบริเวณที่มีน้ำเต็ม (Water bulk)?</b></summary>

**เฉลย:** เพราะในน้ำ $\alpha = 1$ ทำให้พจน์ $(1-\alpha) = 0$ ดังนั้นผลคูณทั้งหมดจึงเป็น 0 เทอมนี้จึงทำงานเงียบๆ เฉพาะที่ Interface เท่านั้น
</details>

<details>
<summary><b>Question 2: ถ้าเราตั้ง `cAlpha 0` จะเกิดอะไรขึ้น?</b></summary>

**เฉลย:** เทอมบีบอัดจะหายไป สมการจะกลายเป็นสมการ Advection ธรรมดา ผิวน้ำจะค่อยๆ เบลอและกระจายตัวออกไปเรื่อยๆ ตามเวลา (Numerical Diffusion) จนดูเหมือนน้ำระเหยหรือผสมกับอากาศไปทั่ว
</details>

<details>
<summary><b>Question 3: วัตถุประสงค์หลักของ MULES คืออะไร?</b></summary>

**ตัวเลือก:**
- A) บีบผิวให้คม
- B) ทำให้น้ำไหลเร็วขึ้น
- C) บังคับค่า $\alpha$ ให้อยู่ระหว่าง 0 และ 1

**เฉลย:** **C) บังคับค่า $\alpha$** (Boundedness) เป็นหน้าที่หลักของการเป็น Limiter ส่วนการบีบผิวเป็นหน้าที่ของเทอม Compression ในสมการ
</details>

<details>
<summary><b>Question 4: เมื่อไหร่ควรใช้ nAlphaSubCycles?</b></summary>

**เฉลย:** ควรใช้เมื่อ:
- ต้องการใช้ Time step ที่ใหญ่ขึ้นเพื่อประหยัดเวลาคำนวณ
- Courant number ของ phase $\alpha$ สูงกว่า 0.3
- เกิดปัญหาค่า $\alpha$ แกว่งหรือหลุดกรอบ

ค่าแนะนำ: เริ่มจาก `nAlphaSubCycles 2-3` แล้วเพิ่มจนกว่าจะเสถียร
</details>

---

## How to Apply: Key Takeaways

**สรุปสิ่งที่คุณควรนำไปใช้:**

1. **เริ่มต้นด้วยค่ามาตรฐาน:** ใช้ `cAlpha 1`, `nAlphaCorr 1-2`, และ `MULESCorr yes` สำหรับงานส่วนใหญ่
2. **Monitor Courant Number:** รักษา $Co_{\alpha} < 0.5$ สำหรับ Explicit MULES หรือใช้ Sub-cycling หากต้องการใช้ค่าสูงกว่า
3. **Troubleshoot ตามลำดับ:** หากผิวเบลอ → เพิ่ม cAlpha; หากเกิด wiggles → ลด cAlpha; หากค่าหลุดกรอบ → เพิ่ม nAlphaSubCycles
4. **พิจารณา interIsoFoam:** สำหรับงานวิจัยที่ต้องการความแม่นยำสูงสุด แม่นยำกว่า MULES แบบดั้งเดิม
5. **ตรวจสอบ Mass Balance:** ใช้ `functionObjects` เพื่อ track มวลรวมของ phase ทุก time step เพื่อยืนยันว่า MULES ทำงานถูกต้อง

---

## 📖 เอกสารที่เกี่ยวข้อง

*   **บทก่อนหน้า**: [01_The_VOF_Concept.md](01_The_VOF_Concept.md)
*   **บทถัดไป**: [03_Setting_Up_InterFoam.md](03_Setting_Up_InterFoam.md)