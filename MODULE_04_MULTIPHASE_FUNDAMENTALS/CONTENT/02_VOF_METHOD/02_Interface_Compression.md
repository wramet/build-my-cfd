# การบีบอัดผิวหน้าและ MULES (Interface Compression & MULES)

> [!TIP] **ทำไมต้องเรียนรู้เรื่องนี้?**
> การบีบอัดผิวหน้า (Interface Compression) และ MULES คือหัวใจสำคัญที่ทำให้การจำลองกระแส 2 เฟสด้วย VOF ใน OpenFOAM ประสบความสำเร็จได้จริง หากไม่มีเทคนิคเหล่านี้ ผิวน้ำจะเบลอและกระจายตัวไปทั่้งโดเมน (Numerical Diffusion) ทำให้ผลลัพธ์ไม่น่าเชื่อถือ การเข้าใจ `cAlpha`, `nAlphaCorr`, และ `nAlphaSubCycles` จะช่วยให้คุณควบคุมความคมของผิวน้ำและเสถียรภาพของการคำนวณได้อย่างมืออาชีพ

ปัญหาโลกแตกของวิธีการ **Volume of Fluid (VOF)** แบบดั้งเดิมคือ "ผิวเบลอ" (Numerical Diffusion) จากการแก้สมการ Transport
OpenFOAM แก้ปัญหานี้ด้วยวิธีที่ชาญฉลาดมาก คือการเพิ่ม "เทอมพิเศษ" เพื่อบีบให้ผิวคมชัด และใช้อัลกอริทึม **MULES** เพื่อป้องกันค่าหลุดกรอบ

---

## 1. วิธีแก้ปัญหาผิวเบลอ (The Compression Term)

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **การกำหนด Discretization Scheme** ในไฟล์ `system/fvSchemes`:
> - **divSchemes**: การ discretize เทอม advection $\nabla \cdot (\mathbf{U} \alpha)$ ใช้ `Gauss vanLeer` หรือ `Gauss linearDiv`
> - **การเพิ่มเทอม Compression**: เทอม $\nabla \cdot (\mathbf{U}_r \alpha (1-\alpha))$ ถูกเพิ่มโดยอัตโนมัติใน solver ผ่านคลาส `MULES`
> - **Field**: ค่า $\alpha$ ถูกเก็บในไฟล์ `0/alpha.water` (หรือ phase อื่นๆ)
>
> ที่มาของสมการนี้อยู่ใน source code ที่ `src/finiteVolume/interpolation/interpolationSchemes/` และ `src/transportModels/geometricVoF/`

แทนที่จะใช้เทคนิคทางเรขาคณิตที่ซับซ้อน (อย่าง PLIC - Piecewise Linear Interface Calculation) OpenFOAM เลือกที่จะ **แก้สมการคณิตศาสตร์เพิ่มอีกเทอม**:

$$ \frac{\partial \alpha}{\partial t} + \nabla \cdot (\mathbf{U} \alpha) + \underbrace{\nabla \cdot (\mathbf{U}_r \alpha (1-\alpha))}_{\text{The Magic Term}} = 0 $$

### เจาะลึกกลไกของ "เทอมวิเศษ"
1.  **Active only at Interface:** สังเกตเทอม $\alpha(1-\alpha)$
    - ในน้ำ ($\alpha=1$) $\rightarrow 1(0) = 0$
    - ในอากาศ ($\alpha=0$) $\rightarrow 0(1) = 0$
    - **ที่รอยต่อ ($0 < \alpha < 1$)** $\rightarrow \text{มีค่า} \neq 0$
    - *ผลลัพธ์:* เทอมนี้จะทำงานเฉพาะจุดที่เป็น Interface เท่านั้น ไม่กระทบส่วนอื่น

2.  **Compression Velocity ($\mathbf{U}_r$):**
    เป็นความเร็วเสมือนที่สร้างขึ้นมาเพื่อ "กด" ไหลเข้าหากันในทิศทางตั้งฉากกับผิว:
    $$ \mathbf{U}_r = \mathbf{n}_{\alpha} \cdot \min(c_{\alpha}|\phi|, |\phi_{max}|) $$
    โดยที่ $\mathbf{n}_{\alpha} = \frac{\nabla \alpha}{|\nabla \alpha|}$ คือเวกเตอร์ตั้งฉากผิวหน้า

3.  **Physical Meaning:**
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

| ค่า `cAlpha` | พฤติกรรม (Behavior) | คำแนะนำ (Recommendation) |
| :---: | :--- | :--- |
| **0** | ปิดการบีบอัด | ไม่แนะนำ ผิวจะเบลอเละในไม่กี่ steps ยกเว้นคุณต้องการจำลองการกระจายตัวของสารเคมี (Scalar transport) |
| **1** | **Conservative Compression** | **ค่าแนะนำมาตรฐาน** บีบความเร็วเท่ากับความเร็วการไหลจริง ($\mathbf{U}_r \approx \mathbf{U}$) ให้ผิวคมประมาณ 2-3 Cells และรักษา Boundedness ได้ดี |
| **> 1** | Over-Compression | บีบแรงกว่าปกติ ผิวจะคมกริบ (1-2 Cells) แต่อาจเกิด **Wiggles** (รอยหยัก) หรือฟองอากาศปลอมๆ ได้ เหมาะกับงาน Static หรือ Quasi-static |

> [!WARNING] **อย่าปรับเพลิน!**
> ค่า `cAlpha` ที่สูงเกินไป (> 1.5) อาจทำให้เกิดแรง Parastic Currents ที่รุนแรง และทำให้ Solver ลู่เข้ายากขึ้น

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
1.  **Boundedness:** $0 \le \alpha \le 1$ เสมอ (ห้ามมีค่าน้ำ -0.1 หรือ 1.2 เด็ดขาด)
2.  **Mass Conservation:** มวลรวมของน้ำในระบบต้องเท่าเดิมเป๊ะๆ ไม่ว่าจะผ่านไปกี่ล้าน Time steps

### กลไกการทำงาน: FCT (Flux Corrected Transport)
MULES ทำงานคล้ายกับเทคนิค FCT คือ:
1.  คำนวณ High-order flux (แม่นยำแต่แกว่ง)
2.  คำนวณ Low-order flux (เสถียรแต่เบลอ)
3.  ผสมสองค่านี้เข้าด้วยกันโดยมีตัวคูณ $\lambda$ (Limiter coefficient) เพื่อให้ได้ค่าที่ดีที่สุดที่ไม่เกินขอบเขต [0, 1]

```mermaid
flowchart TD
    Raw[Calculate Raw Fluxes] --> Limit{Check Bounds [0,1]}
    Limit -- OK --> Accept[Use High-Order Flux (Sharp)]
    Limit -- Violation --> Correct[Reduce Flux with Limiter (Stable)]
    Correct --> CheckGlobal[Global Mass Check]
    CheckGlobal --> Final[Update Alpha]
```

---

## 4. การตั้งค่า VOF ขั้นเทพ (Advanced Configuration)

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

### เคล็ดลับ Sub-cycling (`nAlphaSubCycles`)

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

---

## 5. ตระกูลของ MULES

> [!NOTE] **📂 OpenFOAM Context**
> การเลือกใช้ VOF solver ที่ต่างกันขึ้นอยู่กับ:
> - **interFoam**: ใช้ Explicit MULES แบบดั้งเดิม (Standard VOF)
> - **interIsoFoam**: ใช้ isoAdvector (Geometric reconstruction) ไม่ต้องตั้ง `cAlpha`
> - **interDyMFoam**: สำหรับ mesh that moves/deforms
> - **multiphaseInterFoam**: สำหรับหลาย phase (> 2 phases)
>
> ดูตัวอย่างการใช้งาน solver ต่างๆ ได้ใน `tutorials/multiphase/`

OpenFOAM มีวิวัฒนาการ MULES หลายเวอร์ชัน:

1.  **Explicit MULES (Original):** แม่นยำที่สุด แต่จำกัดที่ $Co_{\alpha} < 0.5$ เพื่อความเสถียร
2.  **Semi-Implicit MULES (Newer):** ผ่อนปรนเงื่อนไข Courant number ได้บ้าง ($Co \approx 1-2$) แต่ความคมอาจลดลงเล็กน้อย
3.  **isoAdvector (interIsoFoam):** **(Game Changer!)** ไม่ใช้ MULES แบบบีบอัด แต่ใช้เทคนิค Geometric Reconstruction จริงๆ (ตัดระนาบในเซลล์) ทำให้ผิวคมกริบภายใน 1 Cell โดยไม่ต้องปรับ `cAlpha`
    - *แนะนำให้ลองใช้ `interIsoFoam` หากต้องการความแม่นยำระดับงานวิจัย*

---

## 🧠 Concept Check: ทดสอบความเข้าใจ

1.  **ทำไมเทอมบีบอัด $\nabla \cdot (\mathbf{U}_r \alpha (1-\alpha))$ ถึงไม่มีผลในบริเวณที่มีน้ำเต็ม (Water bulk)?**
    <details>
    <summary>เฉลย</summary>
    เพราะในน้ำ $\alpha = 1$ ทำให้พจน์ $(1-\alpha) = 0$ ดังนั้นผลคูณทั้งหมดจึงเป็น 0 เทอมนี้จึงทำงานเงียบๆ เฉพาะที่ Interface เท่านั้น
    </details>

2.  **ถ้าเราตั้ง `cAlpha 0` จะเกิดอะไรขึ้น?**
    <details>
    <summary>เฉลย</summary>
    เทอมบีบอัดจะหายไป สมการจะกลายเป็นสมการ Advection ธรรมดา ผิวน้ำจะค่อยๆ เบลอและกระจายตัวออกไปเรื่อยๆ ตามเวลา (Numerical Diffusion) จนดูเหมือนน้ำระเหยหรือผสมกับอากาศไปทั่ว
    </details>

3.  **วัตถุประสงค์หลักของ MULES คืออะไร? (เลือกข้อที่ถูกที่สุด)**
    - A) บีบผิวให้คม
    - B) ทำให้น้ำไหลเร็วขึ้น
    - C) บังคับค่า $\alpha$ ให้อยู่ระหว่าง 0 และ 1
    <details>
    <summary>เฉลย</summary>
    **C) บังคับค่า $\alpha$** (Boundedness) เป็นหน้าที่หลักของการเป็น Limiter ส่วนการบีบผิวเป็นหน้าที่ของเทอม Compression ในสมการ
    </details>

---

## 📖 เอกสารที่เกี่ยวข้อง

*   **บทก่อนหน้า**: [01_The_VOF_Concept.md](01_The_VOF_Concept.md)
*   **บทถัดไป**: [03_Setting_Up_InterFoam.md](03_Setting_Up_InterFoam.md)