# วิธีปริมาตรของไหล และ interFoam (The VOF Method & interFoam)

## ที่คุณจะได้เรียนรู้ (What You Will Learn)

> [!NOTE] **📂 OpenFOAM Context**
> เป้าหมายการเรียนรู้เหล่านี้สอดคล้องกับ **การตั้งค่า Case** จริงใน OpenFOAM:
> - **MULES & cAlpha:** พารามิเตอร์ใน **`system/fvSolution`** ที่ควบคุมความคมชัดของ Interface
> - **setFields:** เครื่องมือ Utility สำหรับกำหนดค่าเริ่มต้นของ **`alpha.water`** field
> - **Courant Number:** ถูกควบคุมใน **`system/controlDict`** ด้วยคีย์เวิร์ด `maxCo`

เมื่อสิ้นสุดบทเรียนนี้ วิศวกรจะสามารถ:

1. **Master Concepts:** เข้าใจกลไกทางคณิตศาสตร์ของตัวแปร $\alpha$ และสมการ Transport
2. **Understand MULES:** อธิบายว่าทำไม OpenFOAM ถึงใช้เทคนิค MULES เพื่อบีบอัด Interface ให้คมชัด
3. **Setup Cases:** ตั้งค่า `interFoam` อย่างถูกต้อง ตั้งแต่ `setFields` ไปจนถึง `fvSolution`
4. **Control Stability:** จัดการ Time-step แบบ Adaptive เพื่อรักษา Courant Number ($Co$) ให้ปลอดภัย
5. **Identify Regimes:** รู้ว่าเมื่อไหร่ควรใช้ VOF และเมื่อไหร่ควรใช้วิธีอื่น (เช่น Eulerian-Eulerian)

---

## ที่ต้องรู้ก่อน (Prerequisites)

> [!NOTE] **📂 OpenFOAM Context**
> ทักษะพื้นฐานเหล่านี้จำเป็นก่อนเริ่มตั้งค่า interFoam Case

ควรมีความรู้พื้นฐานดังนี้:

1. **Navier-Stokes Fundamentals:** ความเข้าใจพื้นฐานเรื่องสมการ Continuity และ Momentum สำหรับ Single-phase flow
2. **OpenFOAM Case Structure:** ความคุ้นเคยกับโครงสร้าง directory (`0/`, `constant/`, `system/`) และไฟล์พื้นฐาน
3. **Finite Volume Method:** ความเข้าใจเรื่อง Discretization และ Flux ผ่าน Cell Faces
4. **Basic CFD Concepts:** ความเข้าใจเรื่อง Courant Number, Convergence และ Boundary Conditions แบบพื้นฐาน

---

## ทำไมต้องเรียนรู้ VOF Method? (Why This Matters)

> [!TIP] **ทำไมต้องเรียนรู้ VOF Method?**
> เทคนิค VOF คือหัวใจสำคัญของการจำลอง **Free Surface Flows** ใน OpenFOAM หากคุณต้องการคำนวณการไหลของน้ำที่มีผิวน้ำชัดเจน เช่น คลื่นน้ำ การแตกของเขื่อน หรือการไหลของน้ำมันในถัง คุณ **ต้อง** เข้าใจ VOF เพราะ:
> - ความแม่นยำในการติดตามผิวน้ำ (Interface Capturing) ขึ้นอยู่กับการตั้งค่า `cAlpha` และการเลือก Scheme การแก้สมการ Alpha
> - ความเสถียรของการจำลองขึ้นอยู่กับการควบคุม Courant Number ผ่าน `maxCo` ใน `controlDict`
> - คุณสมบัติทางกายภาพที่ถูกต้อง (Surface Tension, Density, Viscosity) ถูกกำหนดใน `constant/transportProperties`

**Volume of Fluid (VOF)** คือเทคนิคมาตรฐานระดับอุตสาหกรรมในโลก CFD สำหรับการจำลองการไหลแบบหลายเฟสที่มี **พื้นผิวอิสระ (Free Surface)** ชัดเจน ไม่ว่าจะเป็นการแตกของเขื่อนที่รุนแรง, คลื่นยักษ์ในมหาสมุทร, หรือฟองอากาศละเอียดในเครื่องดื่มอัดลม

OpenFOAM นำเสนอวิธี VOF ผ่าน Solver ตระกูล `interFoam` ซึ่งยกย่องว่าเป็นหนึ่งใน Solver แบบโอเพ่นซอร์สที่เสถียรและแม่นยำที่สุดสำหรับการจับภาพรอยต่อของไหล (Interface Capturing)

---

## 🌊 ทำไมต้อง VOF? (Why VOF?)

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้อธิบาย **แนวคิดพื้นฐาน** ของ VOF ที่จำเป็นต้องเข้าใจก่อนเริ่มตั้งค่า OpenFOAM แนวคิดเรื่อง "Digital Photo" นี้คือพื้นฐานของการตีความค่า **`alpha.water`** field ใน directory **`0/`** ซึ่งเป็น field หลักที่ interFoam ใช้ในการติดตามผิวน้ำ

การไหลแบบหลายเฟสมีหลายรูปแบบ (เช่น ก๊าซผสมกับของเหลวแบบเนียนๆ หรือแยกชั้นกันชัดเจน) VOF ถูกออกแบบมาเพื่อกรณีที่ **"รอยต่อต้องคมชัด"**

> [!TIP] **Physical Analogy: The Digital Photo (ภาพถ่ายดิจิทัล)**
>
> ลองจินตนาการว่าคุณถ่ายรูปแก้วน้ำที่มีน้ำอยู่ครึ่งแก้วด้วยกล้องดิจิทัล:
> - **Grid/Mesh:** คือ พิกเซล (Pixels) ของภาพ
> - **Phase Fraction ($\alpha$):** คือ ค่าความสว่างหรือสีของแต่ละพิกเซล
>   - **$\alpha = 1$ (สีดำสนิท):** พิกเซลนั้นมี **น้ำ** เต็ม 100%
>   - **$\alpha = 0$ (สีขาวสนิท):** พิกเซลนั้นมี **อากาศ** เต็ม 100%
>   - **$0 < \alpha < 1$ (สีเทา):** พิกเซลนั้นอยู่ตรง **ผิวหน้าน้ำ** (Interface) พอดี
>
> **ภารกิจของ VOF:** คือการคำนวณว่า "สีเทา" นี้ควรจะเคลื่อนที่ไปทางไหนในเฟรมถัดไป โดยพยายามรักษาเส้นขอบระหว่างสีขาวและดำให้ **"คม"** ที่สุด ไม่ให้กลายเป็นภาพเบลอๆ (Numerical Diffusion)

---

## 🛠️ ขั้นตอนการทำงาน (VOF Workflow)

> [!NOTE] **📂 OpenFOAM Context**
> Workflow นี้แสดง **ลำดับไฟล์และ Directory** ที่คุณต้องจัดการใน interFoam case:
> - **`constant/transportProperties`**: กำหนดค่า `rho`, `mu`, `sigma` สำหรับทั้ง 2 เฟส
> - **`0/alpha.water`**: Field เริ่มต้นที่สร้างด้วย `setFieldsDict`
> - **`system/controlDict`**: ตั้งค่า `adjustTimeStep` และ `maxCo` เพื่อความเสถียร
> - **`system/fvSolution`**: ตั้งค่า `MULES` และ `nAlphaCorr` สำหรับการแก้สมการ Alpha
> - **`system/fvSchemes`**: เลือก `divSchemes` สำหรับ `div(phi,alpha)`

กระบวนการจำลอง VOF ใน OpenFOAM มีขั้นตอนเฉพาะที่แตกต่างจาก Single-phase flow:

```mermaid
graph TD
    classDef config fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef solver fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    
    Start((Start)) --> Mesh[1. Mesh Generation<br>Refine @ Expected Interface]
    Mesh --> Transport[2. transportProperties<br>Define Rho, Nu, Sigma]
    Transport --> Init[3. setFields<br>Paint the initial Alpha]:::config
    Init --> Solver{4. Run interFoam}:::solver
    
    Solver --> AlphaEqn[Solve Alpha Equation<br>with MULES Compression]:::solver
    AlphaEqn --> Props[Update Mixture Properties<br>Rho = alpha*rho1 + (1-alpha)*rho2]:::solver
    Props --> PISO[PISO Loop<br>Solve P-U Coupling]:::solver
    
    PISO --> Convergence{Converged?}
    Convergence -- No --> PISO
    Convergence -- Yes --> Time{End Time?}
    
    Time -- No --> AdaptTime[Adjust Time Step<br>Maintain Co < 1]:::config
    AdaptTime --> Solver
    Time -- Yes --> Post[5. Post-processing<br>Contour Alpha = 0.5]
```

---

## 📐 สมการพื้นฐาน (Governing Equations)

> [!NOTE] **📂 OpenFOAM Context**
> สมการเหล่านี้คือ **พื้นฐานทางคณิตศาสตร์** ที่ถูก implement ใน interFoam solver:
> - **Phase Fraction Transport:** ถูกแก้ด้วย `MULES::explicitSolve` ใน solver code
> - **Mixture Properties:** ถูกคำนวณอัตโนมัติใน `createFields.H` และใช้ค่าจาก **`constant/transportProperties`**
> - **Momentum Equation:** ใช้ `p_rgh` แทน `p` ใน **`0/p_rgh`** field และ Boundary Conditions
> - **Surface Tension:** ถูกคำนวณจากค่า `sigma` ใน `transportProperties` และใช้ผ่าน `fvc::grad(alpha)`

VOF ไม่ได้แก้สมการของแต่ละเฟสแยกกัน (เหมือน Eulerian-Eulerian) แต่แก้สมการของ **"ของไหลผสม (Mixture)"** เพียงชุดเดียว:

### 1. สมการสัดส่วนเฟส (Phase Fraction Transport)

> [!NOTE] **📂 OpenFOAM Context**
> ใน OpenFOAM สมการนี้ถูกแก้โดยใช้ **MULES** (Multidimensional Universal Limiter with Explicit Solution) ซึ่งถูกกำหนดค่าใน **`system/fvSolution`**:
> ```openfoam
> solvers
> {
>     alpha.water
>     {
>         nAlphaCorr      2;
>         nAlphaSubCycles 2;
>         cAlpha          1;
>     }
> }
> ```
> พารามิเตอร์ `cAlpha` คือสัมประสิทธิ์การบีบอัด Interface ซึ่งจะอธิบายรายละเอียดใน **[[02_Interface_Compression]]**

หัวใจของ VOF คือการติดตามค่า $\alpha$ (Volume Fraction ของน้ำ):

$$ \frac{\partial \alpha}{\partial t} + \nabla \cdot (\mathbf{U} \alpha) + \underbrace{\nabla \cdot (\mathbf{U}_r \alpha (1-\alpha))}_{\text{compression term}} = 0 $$

*   **เทอมที่ 1-2:** การพาน้ำไปตามกระแสไหลปกติ
*   **เทอมที่ 3 (เฉพาะ OpenFOAM):** เทอมพิเศษที่ช่วย "บีบ" (Compress) ให้รอยต่อคมชัดขึ้น มีค่าเฉพาะที่ Interface (เพราะ $\alpha(1-\alpha)$ เป็นศูนย์ที่อื่น)

### 2. คุณสมบัติของผสม (Mixture Properties)

> [!NOTE] **📂 OpenFOAM Context**
> ในไฟล์ **`constant/transportProperties`** คุณต้องกำหนดคุณสมบัติของแต่ละเฟส:
> ```openfoam
> phases
> (
>     water
>     {
>         transportModel  Newtonian;
>         nu              [0 2 -1 0 0 0 0] 1e-06;
>         rho             [1 -3 0 0 0 0 0] 1000;
>     }
>     air
>     {
>         transportModel  Newtonian;
>         nu              [0 2 -1 0 0 0 0] 1.48e-05;
>         rho             [1 -3 0 0 0 0 0] 1;
>     }
> );
> sigma           [1 0 -2 0 0 0 0] 0.07;
> ```
> OpenFOAM จะคำนวณค่าผสมอัตโนมัติตามสมการข้างต้น

เมื่อรู้ค่า $\alpha$ เราจะคำนวณคุณสมบัติเฉลี่ยในเซลล์นั้น:

$$ \rho = \alpha \rho_{water} + (1-\alpha) \rho_{air} $$
$$ \mu = \alpha \mu_{water} + (1-\alpha) \mu_{air} $$

### 3. สมการโมเมนตัมเดียว (Single Momentum Equation)

> [!NOTE] **📂 OpenFOAM Context**
> สมการนี้คือ core ของ interFoam solver ที่คุณจะเห็นในไฟล์ source code:
> - Field **`U`** (velocity) ถูกเก็บใน directory **`0/`**
> - Field **`p_rgh`** (pressure minus hydrostatic) ถูกเก็บใน **`0/p_rgh`**
> - Boundary Conditions สำหรับ `p_rgh` ต้องตั้งค่าเป็น `fixedFluxPressure` หรือ `totalPressure` สำหรับ Free Surface problems
> - แรง Surface Tension **$\mathbf{F}_{st}$** ถูกคำนวณโดย Automatic จากค่า `sigma` ใน transportProperties

$$ \frac{\partial (\rho \mathbf{U})}{\partial t} + \nabla \cdot (\rho \mathbf{U} \mathbf{U}) = -\nabla p_{rgh} - \mathbf{g} \cdot \mathbf{x} \nabla \rho + \nabla \cdot \tau + \mathbf{F}_{st} $$

*   **$p_{rgh}$:** ความดันที่หักลบ Hydrostatic pressure ออกแล้ว (เพื่อให้ตั้งค่า BC ง่ายขึ้น)
*   **$\mathbf{F}_{st}$:** แรงตึงผิว (Surface Tension Force) ที่กระทำเฉพาะที่ผิวหน้า

---

## 🏭 การใช้งานในโลกจริง (Real-World Applications)

> [!NOTE] **📂 OpenFOAM Context**
> การนำ VOF ไปใช้ใน Application ต่างๆ จะมีผลต่อ **การตั้งค่า Mesh และ Boundary Conditions**:
> - **Ship Hull:** ต้องใช้ **`refinementSurface`** ใน **`system/snappyHexMeshDict`** เพื่อละเอียดผิวน้ำรอบๆ เรือ
> - **Dam Break:** ต้องตั้งค่า `setFieldsDict` ให้สร้าง column น้ำสูง และใช้ `maxCo` ต่ำๆ เพื่อเสถียร
> - **Slug Flow:** ต้องตั้งค่า **`inlet`** boundary conditions สำหรับ `alpha.water` ให้เป็น `fixedValue` แบบ time-varying

| อุตสาหกรรม | การใช้งาน (Application) | สิ่งที่ VOF ตอบโจทย์ |
| :--- | :--- | :--- |
| **Marine** | **Ship Hull Resistance** | คำนวณแรงต้านคลื่นที่หัวเรือ, ดูการกระเซ็นของน้ำ |
| **Civil** | **Dam Break / Spillway** | ออกแบบทางระบายน้ำล้น, ดูผลกระทบน้ำท่วม |
| **Oil & Gas** | **Slug Flow in Pipes** | จำลองก้อนน้ำมันสลับก๊าซในท่อส่ง |
| **Automotive** | **Tank Sloshing** | ศึกษาการกระฉอกของน้ำมันในถังขณะรถเบรก |
| **Manufacturing**| **Inkjet Printing** | ดูการหยดของหมึกพิมพ์และการกระจายตัวบนกระดาษ |

---

## 📚 เนื้อหาในโมดูล (Module Structure)

> [!NOTE] **📂 OpenFOAM Context**
> โครงสร้างเนื้อหานี้ออกแบบมาเพื่อให้คุณ **เรียนตามลำดับ Case Setup** จริง:
> - **01_VOF_Concept:** เข้าใจทฤษฎี → ตีความค่า **`alpha.water`** ใน directory **`0/`**
> - **02_Interface_Compression:** เข้าใจ MULES → ตั้งค่า **`system/fvSolution`** อย่างถูกต้อง
> - **03_Setting_Up_InterFoam:** ปฏิบัติจริง → สร้าง Case ตั้งแต่ `transportProperties` ถึง `fvSchemes`
> - **04_Adaptive_Time_Stepping:** เพิ่มเสถียรภาพ → ตั้งค่า **`system/controlDict`** เพื่อปรับ `deltaT` อัตโนมัติ

| ไฟล์ | เนื้อหาหลัก | เวลาอ่านโดยประมาณ |
| :--- | :--- | :--- |
| **[[01_The_VOF_Concept]]** | เจาะลึกทฤษฎีพื้นฐาน, การตีความค่า Alpha, และสิ่งที่ทำให้ VOF ต่างจากวิธีอื่น | 15 นาที |
| **[[02_Interface_Compression]]** | ศาสตร์แห่งความคมชัด - เข้าใจการทำงานของ MULES Algorithm และพารามิเตอร์ `cAlpha` | 20 นาที |
| **[[03_Setting_Up_InterFoam.md]]** | คู่มือปฏิบัติ - การตั้งค่า `transportProperties`, `setFields` และ Boundary Conditions สำหรับ `p_rgh` | 25 นาที |
| **[[04_Adaptive_Time_Stepping]]** | เทคนิคการจัดการเวลา - ทำไม $Co < 1$ ถึงเป็นกฎเหล็ก และวิธีตั้งค่า `controlDict` ให้ปรับเวลาอัตโนมัติ | 15 นาที |

---

## 🧠 Concept Check (ทดสอบความเข้าใจ)

> [!NOTE] **📂 OpenFOAM Context**
> คำถามเหล่านี้ออกแบบมาเพื่อทดสอบความเข้าใจที่จำเป็นก่อน **ตั้งค่า interFoam Case**:
> - คำถามที่ 1: ตีความค่า `alpha.water` ใน directory **`0/`**
> - คำถามที่ 2: เปรียบเทียบ VOF vs Eulerian-Eulerian → ช่วยเลือก **Solver** ที่เหมาะสม
> - คำถามที่ 3: เข้าใจปัญหา **Numerical Diffusion** → จำเป็นต้องตั้งค่า **`cAlpha`** อย่างถูกต้อง

<details>
<summary><b>❓ คำถามที่ 1: ถ้าเซลล์หนึ่งมีค่า $\alpha = 0.5$ แปลว่าอะไร?</b></summary>

**เฉลย:** หมายความว่าเซลล์นั้นมีน้ำอยู่ 50% และอากาศ 50% ซึ่งในทาง Computational หมายถึงตำแหน่งของ "ผิวหน้า" (Interface) ของของเหลว

**🔗 OpenFOAM Connection:** เมื่อคุณเปิดไฟล์ **`0/alpha.water`** และเห็นค่า `0.5` อยู่บางจุด นั่นคือตำแหน่งที่ผิวน้ำตัดผ่านเซลล์นั้น
</details>

<details>
<summary><b>❓ คำถามที่ 2: ทำไม VOF ถึงประหยัดทรัพยากรกว่า Eulerian-Eulerian (Two-Fluid Model)?</b></summary>

**เฉลย:** เพราะ VOF แก้สมการโมเมนตัมเพียง **ชุดเดียว** (สำหรับ Mixture) ในขณะที่ E-E ต้องแก้สมการโมเมนตัมสำหรับ **ทุกเฟส** แยกกัน ทำให้ VOF คำนวณเร็วกว่ามากสำหรับงาน Free Surface

**🔗 OpenFOAM Connection:** ใน OpenFOAM คุณจะใช้ solver ต่างกัน: `interFoam` (VOF) สำหรับ free surface หรือ `twoPhaseEulerFoam` (E-E) สำหรับ dispersed flows
</details>

<details>
<summary><b>❓ คำถามที่ 3: อะไรคือศัตรูตัวฉกาจที่สุดของการจำลอง VOF?</b></summary>

**เฉลย:** **Numerical Diffusion (การแพร่เชิงตัวเลข)** ซึ่งทำให้หน้าสัมผัสน้ำ-อากาศที่ควรจะคมชัด กลายเป็นแถบเบลอๆ หนาๆ ทำให้ระบุตำแหน่งผิวน้ำไม่ได้ และฟิสิกส์ผิดเพี้ยน

**🔗 OpenFOAM Connection:** นี่คือเหตุผลที่คุณต้องตั้งค่า `cAlpha` ใน **`system/fvSolution`** และเลือก `divSchemes` ที่เหมาะสมใน **`system/fvSchemes`** เพื่อต่อสู้ Numerical Diffusion
</details>

---

## 🎯 สรุปสิ่งสำคัญ (Key Takeaways)

### วิธีนำไปประยุกต์ใช้ (How to Apply)

> [!NOTE] **📂 OpenFOAM Context**
> แนวทางการนำความรู้ไปใช้ในการตั้งค่า Case จริง

**Action Items สำหรับการตั้งค่า interFoam Case:**

1. **✅ เลือก Solver ที่เหมาะสม:**
   - ใช้ `interFoam` เมื่อ: มี Free Surface ชัดเจน (เช่น คลื่นน้ำ, Dam Break)
   - ใช้ `multiphaseInterFoam` เมื่อ: มีมากกว่า 2 เฟส
   - **หลีกเลี่ยง** Eulerian-Eulerian สำหรับ Free Surface flows

2. **✅ กำหนดค่าใน `system/fvSolution`:**
   ```openfoam
   solvers
   {
       alpha.water
       {
           nAlphaCorr      2;      // เพิ่มความคมชัด
           nAlphaSubCycles 2;      // เพิ่มเสถียรภาพ
           cAlpha          1;      // ค่าปกติ (0-1)
       }
   }
   ```

3. **✅ ควบคุม Courant Number ใน `system/controlDict`:**
   ```openfoam
   application     interFoam;
   startFrom       startTime;
   
   adjustTimeStep  yes;
   maxCo           0.5;    // แนะนำ 0.3-0.5 สำหรับ VOF
   maxAlphaCo      0.5;    // Co เฉพาะที่ Interface
   ```

4. **✅ ตั้งค่า `constant/transportProperties`:**
   - กำหนด `rho`, `nu` สำหรับแต่ละ phase ให้ถูกต้อง
   - กำหนด `sigma` (Surface Tension Coefficient) ให้ตรงกับ material pair

5. **✅ สร้าง Initial Condition ด้วย `setFields`:**
   - สร้างไฟล์ `system/setFieldsDict`
   - "วาดรูป" รูปทรงเริ่มต้นของน้ำด้วย `boxToCell` หรือ `surfaceToCell`

### ⚠️ ข้อควรระวัง (Common Pitfalls)

| ปัญหา | สาเหตุ | วิธีแก้ |
| :--- | :--- | :--- |
| **Interface เบลอหนา** | `cAlpha` ต่ำเกินไป หรือใช้ `Gauss` scheme | เพิ่ม `cAlpha` หรือใช้ `Gauss vanLeer` |
| **Simulation ระเบิด** | `maxCo` สูงเกินไป | ลด `maxCo` ให้ < 0.5 |
| **ผลลัพธ์ไม่ Converge** | `nAlphaCorr` ต่ำเกินไป | เพิ่มเป็น 2-3 |
| **Surface Tension ผิด** | กำหนด `sigma` ผิดหน่วย | ตรวจสอบ units: `[1 0 -2 0 0 0 0]` |

### 📋 Parameters Quick Reference

| พารามิเตอร์ | ตำแหน่ง | ค่าแนะนำ | ผลกระทบ |
| :--- | :--- | :--- | :--- |
| **cAlpha** | `system/fvSolution` | 0.5 - 1.0 | ยิ่งสูง Interface ยิ่งคม แต่อาจไม่เสถียร |
| **maxCo** | `system/controlDict` | 0.3 - 0.5 | ยิ่งต่ำเสถียรยิ่งดี แต่คำนวณช้า |
| **maxAlphaCo** | `system/controlDict` | 0.3 - 0.5 | Co เฉพาะที่ Interface (สำคัญมาก) |
| **nAlphaCorr** | `system/fvSolution` | 1 - 3 | ยิ่งสูงคมและเสถียร แต่คำนวณช้า |
| **nAlphaSubCycles** | `system/fvSolution` | 1 - 5 | เพิ่มเสถียรภาพสำหรับ flow เร็วๆ |

---

## 📖 เอกสารที่เกี่ยวข้อง

*   **บทก่อนหน้า**: [../01_FUNDAMENTAL_CONCEPTS/02_Interfacial_Phenomena.md](../01_FUNDAMENTAL_CONCEPTS/02_Interfacial_Phenomena.md)
*   **บทถัดไป**: [01_The_VOF_Concept.md](01_The_VOF_Concept.md)