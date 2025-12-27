# วิธีปริมาตรของไหล และ interFoam (The VOF Method & interFoam)

**Volume of Fluid (VOF)** คือเทคนิคมาตรฐานระดับอุตสาหกรรมในโลก CFD สำหรับการจำลองการไหลแบบหลายเฟสที่มี **พื้นผิวอิสระ (Free Surface)** ชัดเจน ไม่ว่าจะเป็นการแตกของเขื่อนที่รุนแรง, คลื่นยักษ์ในมหาสมุทร, หรือฟองอากาศละเอียดในเครื่องดื่มอัดลม

OpenFOAM นำเสนอวิธี VOF ผ่าน Solver ตระกูล `interFoam` ซึ่งยกย่องว่าเป็นหนึ่งใน Solver แบบโอเพ่นซอร์สที่เสถียรและแม่นยำที่สุดสำหรับการจับภาพรอยต่อของไหล (Interface Capturing)

---

## 🌟 ทำไมต้อง VOF? (Why VOF?)

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

## 🎯 วัตถุประสงค์การเรียนรู้ (Learning Objectives)

เมื่อสิ้นสุดบทเรียนนี้ วิศวกรจะสามารถ:

1.  **Master Concepts:** เข้าใจกลไกทางคณิตศาสตร์ของตัวแปร $\alpha$ และสมการ Transport
2.  **Understand MULES:** อธิบายว่าทำไม OpenFOAM ถึงใช้เทคนิค MULES เพื่อบีบอัด Interface ให้คมชัด
3.  **Setup Cases:** ตั้งค่า `interFoam` อย่างถูกต้อง ตั้งแต่ `setFields` ไปจนถึง `fvSolution`
4.  **Control Stability:** จัดการ Time-step แบบ Adaptive เพื่อรักษา Courant Number ($Co$) ให้ปลอดภัย
5.  **Identify Regimes:** รู้ว่าเมื่อไหร่ควรใช้ VOF และเมื่อไหร่ควรใช้วิธีอื่น (เช่น Eulerian-Eulerian)

---

## 🛠️ ขั้นตอนการทำงาน (VOF Workflow)

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

VOF ไม่ได้แก้สมการของแต่ละเฟสแยกกัน (เหมือน Eulerian-Eulerian) แต่แก้สมการของ **"ของไหลผสม (Mixture)"** เพียงชุดเดียว:

### 1. สมการสัดส่วนเฟส (Phase Fraction Transport)

หัวใจของ VOF คือการติดตามค่า $\alpha$ (Volume Fraction ของน้ำ):

$$ \frac{\partial \alpha}{\partial t} + \nabla \cdot (\mathbf{U} \alpha) + \underbrace{\nabla \cdot (\mathbf{U}_r \alpha (1-\alpha))}_{\text{compression term}} = 0 $$

*   **เทอมที่ 1-2:** การพาน้ำไปตามกระแสไหลปกติ
*   **เทอมที่ 3 (เฉพาะ OpenFOAM):** เทอมพิเศษที่ช่วย "บีบ" (Compress) ให้รอยต่อคมชัดขึ้น มีค่าเฉพาะที่ Interface (เพราะ $\alpha(1-\alpha)$ เป็นศูนย์ที่อื่น)

### 2. คุณสมบัติของผสม (Mixture Properties)

เมื่อรู้ค่า $\alpha$ เราจะคำนวณคุณสมบัติเฉลี่ยในเซลล์นั้น:

$$ \rho = \alpha \rho_{water} + (1-\alpha) \rho_{air} $$
$$ \mu = \alpha \mu_{water} + (1-\alpha) \mu_{air} $$

### 3. สมการโมเมนตัมเดียว (Single Momentum Equation)

$$ \frac{\partial (\rho \mathbf{U})}{\partial t} + \nabla \cdot (\rho \mathbf{U} \mathbf{U}) = -\nabla p_{rgh} - \mathbf{g} \cdot \mathbf{x} \nabla \rho + \nabla \cdot \tau + \mathbf{F}_{st} $$

*   **$p_{rgh}$:** ความดันที่หักลบ Hydrostatic pressure ออกแล้ว (เพื่อให้ตั้งค่า BC ง่ายขึ้น)
*   **$\mathbf{F}_{st}$:** แรงตึงผิว (Surface Tension Force) ที่กระทำเฉพาะที่ผิวหน้า

---

## 🏭 การใช้งานในโลกจริง (Real-World Applications)

| อุตสาหกรรม | การใช้งาน (Application) | สิ่งที่ VOF ตอบโจทย์ |
| :--- | :--- | :--- |
| **Marine** | **Ship Hull Resistance** | คำนวณแรงต้านคลื่นที่หัวเรือ, ดูการกระเซ็นของน้ำ |
| **Civil** | **Dam Break / Spillway** | ออกแบบทางระบายน้ำล้น, ดูผลกระทบน้ำท่วม |
| **Oil & Gas** | **Slug Flow in Pipes** | จำลองก้อนน้ำมันสลับก๊าซในท่อส่ง |
| **Automotive** | **Tank Sloshing** | ศึกษาการกระฉอกของน้ำมันในถังขณะรถเบรก |
| **Manufacturing**| **Inkjet Printing** | ดูการหยดของหมึกพิมพ์และการกระจายตัวบนกระดาษ |

---

## 📚 เนื้อหาในโมดูล (Module Structure)

*   **[[01_The_VOF_Concept]]**: เจาะลึกทฤษฎีพื้นฐาน, การตีความค่า Alpha, และสิ่งที่ทำให้ VOF ต่างจากวิธีอื่น
*   **[[02_Interface_Compression]]**: ศาสตร์แห่งความคมชัด - เข้าใจการทำงานของ MULES Algorithm และพารามิเตอร์ `cAlpha`
*   **[[03_Setting_Up_InterFoam.md]]**: คู่มือปฏิบัติ - การตั้งค่า `transportProperties`, `setFields` และ Boundary Conditions สำหรับ `p_rgh`
*   **[[04_Adaptive_Time_Stepping]]**: เทคนิคการจัดการเวลา - ทำไม $Co < 1$ ถึงเป็นกฎเหล็ก และวิธีตั้งค่า `controlDict` ให้ปรับเวลาอัตโนมัติ

---

## 🧠 Concept Check (ทดสอบความเข้าใจ)

1.  **ถ้าเซลล์หนึ่งมีค่า $\alpha = 0.5$ แปลว่าอะไร?**
    <details><summary>เฉลย</summary>หมายความว่าเซลล์นั้นมีน้ำอยู่ 50% และอากาศ 50% ซึ่งในทาง Computational หมายถึงตำแหน่งของ "ผิวหน้า" (Interface) ของของเหลว</details>

2.  **ทำไม VOF ถึงประหยัดทรัพยากรกว่า Eulerian-Eulerian (Two-Fluid Model)?**
    <details><summary>เฉลย</summary>เพราะ VOF แก้สมการโมเมนตัมเพียง **ชุดเดียว** (สำหรับ Mixture) ในขณะที่ E-E ต้องแก้สมการโมเมนตัมสำหรับ **ทุกเฟส** แยกกัน ทำให้ VOF คำนวณเร็วกว่ามากสำหรับงาน Free Surface</details>

3.  **อะไรคือศัตรูตัวฉกาจที่สุดของการจำลอง VOF?**
    <details><summary>เฉลย</summary>**Numerical Diffusion (การแพร่เชิงตัวเลข)** ซึ่งทำให้หน้าสัมผัสน้ำ-อากาศที่ควรจะคมชัด กลายเป็นแถบเบลอๆ หนาๆ ทำให้ระบุตำแหน่งผิวน้ำไม่ได้ และฟิสิกส์ผิดเพี้ยน</details>