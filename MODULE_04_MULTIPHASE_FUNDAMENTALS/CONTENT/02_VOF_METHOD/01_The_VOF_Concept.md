# แนวคิดพื้นฐาน VOF (The VOF Concept)

## 🎯 What You Will Learn

เมื่ออ่านบทนี้จบ คุณจะสามารถ:
- **อธิบาย** แนวคิด VOF ผ่านการเปรียบเทียบ Raster vs Vector Graphics
- **คำนวณ** คุณสมบัติของ "ของไหลผสม" (Mixture Properties) จากค่า Phase Fraction
- **เข้าใจ** ปัญหา Numerical Diffusion และผลกระทบต่อ Surface Tension
- **แยกแยะ** ความแตกต่างระหว่าง VOF และวิธีอื่นๆ (Level Set, Eulerian-Eulerian)
- **ประยุกต์** ใช้งาน `alpha.water` field ใน OpenFOAM อย่างเหมาะสม

## 📋 Prerequisites

- **ทักษะพื้นฐาน**: ความเข้าใจเรื่อง Finite Volume Method และ Mesh Structure
- **ไฟล์ที่ควรอ่านก่อน**: [00_Overview.md](00_Overview.md)
- **แนวคิดที่เกี่ยวข้อง**: Navier-Stokes Equations, Discretization Schemes

---

> [!TIP] **Why This Matters**
> การเข้าใจแนวคิด VOF เป็นสิ่งสำคัญมาก เพราะ:
> - **ความเสถียร**: การทำความเข้าใจการกระจายของ α จะช่วยให้คุณป้องกันปัญหาการแตกตัวของการคำนวณ (Divergence)
> - **ความแม่นยำ**: รู้จักกับ Interface Compression จะช่วยรักษาความคมของผิวน้ำให้เป็นธรรมชาติ
> - **ประสิทธิภาพ**: สามารถตั้งค่า Courant Number และ Time Step ได้อย่างเหมาะสม ทำให้การคำนวณเร็วและเสถียร

---

## 💡 The Digital Photo Analogy: Raster vs Vector

> [!NOTE] **📂 OpenFOAM Context**
> แนวคิดนี้เป็นพื้นฐานของ **Domain A: Physics & Fields**
> - **File**: `0/alpha.water` - ไฟล์กำหนดค่าเริ่มต้นของ Phase Fraction
> - **Keywords**: `alpha.water`, `alpha1`, `volScalarField`
> - **Application**: เมื่อคุณเปิดไฟล์ `0/alpha.water` คุณจะเห็นค่า α ที่ถูกกำหนดให้กับแต่ละ Cell บน Mesh

**Volume of Fluid (VOF)** เป็นหัวใจสำคัญของการจำลองการไหลแบบ Free Surface ใน OpenFOAM การทำความเข้าใจ "ปรัชญา" ของมันจะช่วยให้คุณปรับแต่งค่าต่างๆ ได้อย่างมีเหตุผล

ลองนึกภาพคุณกำลังถ่ายรูปวงกลมบนคอมพิวเตอร์ มีสองวิธีในการเก็บข้อมูลนี้:

### Vector Graphics (Lagrangian / Front Tracking)
- **วิธีเก็บ:** เก็บสมการของวงกลม ($x^2 + y^2 = r^2$) หรือเก็บจุดต่อกันเป็นเส้น
- **ข้อดี:** คมชัดกริบ ซูมแค่ไหนก็ไม่แตก
- **ข้อเสีย:** ถ้าวงกลมแตกเป็น 2 วง หรือรวมร่างกับวงกลมอื่น สมการจะซับซ้อนมหาศาล (Topology Change is hard)

### Raster / Pixels (Eulerian / VOF)
- **วิธีเก็บ:** แบ่งหน้าจอเป็นตาราง (Grid) แล้วระบายสีแต่ละช่อง
  - ช่องในวงกลม = สีดำ ($\alpha=1$)
  - ช่องนอกวงกลม = สีขาว ($\alpha=0$)
  - ช่องขอบตัดผ่าน = สีเทา ($0 < \alpha < 1$)
- **ข้อดี:** ไม่สนใจว่าจะมีกี่วง จะแตกหรือรวมก็แค่เปลี่ยนสี (Topology Change is easy)
- **ข้อเสีย:** ภาพจะ "เบลอ" ถ้าตารางไม่ละเอียดพอ

> [!INFO] **VOF = Raster Method**
> VOF ยอมสละความคมชัดระดับอนันต์ เพื่อแลกกับความสามารถในการจำลองการไหลที่ซับซ้อนและรุนแรง (เช่น คลื่นซัดฝั่ง) ได้อย่างทนทาน

---

## 1. Phase Fraction ($\alpha$): The Key Variable

<!-- IMAGE: IMG_04_001 -->
<!-- 
Purpose: เพื่อเปรียบเทียบความแตกต่างระหว่าง "โลกจริง" (Vector/Smooth Interface) กับ "สิ่งที่ OpenFOAM เห็น" (Raster/VOF Field)
Prompt: "Visual analogy diagram: 'Physical Reality vs VOF Representation'. **Left Panel (Physics):** A smooth, continuous wave of water moving through air. The interface is a perfect curve. **Right Panel (VOF/Simulation):** The EXACT same wave overlaid on a coarse Grid. The cells are colored by Liquid Fraction $\alpha$: Pure Blue ($\alpha=1$), Pure White ($\alpha=0$), and Shades of Light Blue ($\alpha \approx 0.5$) at the interface. Highlighting the 'Stair-step' or 'Pixelated' nature of the numeric solution. STYLE: Split-screen infographic, clean flat vector art, contrasting 'Smooth' vs 'Pixelated'."
-->
![[IMG_04_001.JPg]]

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain A: Physics & Fields**
> - **File**: `0/alpha.water` - Field file สำหรับ Phase Fraction
> - **Keywords**: `internalField`, `boundaryField`, `fixedValue`, `zeroGradient`

ใน OpenFOAM ตัวแปรพระเอกคือ `alpha.water` (หรือ `alpha1` ในเวอร์ชันเก่า):

$$ \alpha(\mathbf{x}, t) = \begin{cases} 1 & \text{ถ้าจุดนั้นมีน้ำเต็มๆ} \\ 0 & \text{ถ้าจุดนั้นมีแต่อากาศ} \\ 0 < \alpha < 1 & \text{ถ้าจุดนั้นมี interface} \end{cases} $$

### Physical Interpretation in a Cell
ถ้า Cell หนึ่งมีปริมาตร $V$ และมีค่าน้ำ $\alpha = 0.4$:
- ปริมาตรน้ำ $V_{water} = 0.4 \times V$
- ปริมาตรอากาศ $V_{air} = 0.6 \times V$

> **Note:** VOF ไม่รู้ตำแหน่งที่แน่ชัดของน้ำภายใน Cell มันรู้แค่ "ปริมาณ" รวม เราต้องใช้เทคนิค Reconstruction (เช่น Iso-surface) เพื่อสร้างภาพผิวหน้า

---

## 2. The Mixture Fluid Properties

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain A: Physics & Fields**
> - **File**: `constant/transportProperties` - กำหนดคุณสมบัติทางกายภาพของแต่ละเฟส
> - **Keywords**: `phases`, `transportModel`, `nu`, `rho`
> - **Critical Point**: Density Ratio สูง (1000:1) ส่งผลต่อความเสถียรของ Pressure Solver

VOF ไม่ได้แก้ Navier-Stokes สองรอบ (สำหรับน้ำและอากาศ) แต่แก้รอบเดียวสำหรับ **"ของไหลผสมเสมือน (Effective Fluid)"**:

### Density
$$ \rho = \alpha \rho_{water} + (1-\alpha) \rho_{air} $$

### Dynamic Viscosity
$$ \mu = \alpha \mu_{water} + (1-\alpha) \mu_{air} $$

> [!WARNING] **The Density Jump Challenge**
> สำหรับน้ำและอากาศ, $\rho_{water} \approx 1000$ และ $\rho_{air} \approx 1$
> ที่ Interface, ความหนาแน่นจะกระโดดถึง **1000 เท่า** ในระยะ 1-2 Cells
> นี่คือสาเหตุที่ VOF Solver ต้องมีความเสถียรสูงมาก

---

## 3. The Transport Equation

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain B: Numerics & Linear Algebra**
> - **File**: `system/fvSchemes` - กำหนดรูปแบบ Discretization
> - **Keywords**: `divSchemes`, `Gauss`, `upwind`, `MULES`, `limited`

รอยต่อเคลื่อนที่ไปตามการไหล ($\mathbf{U}$) ตามสมการ Advection:

$$ \frac{\partial \alpha}{\partial t} + \nabla \cdot (\mathbf{U} \alpha) = 0 $$

### The Numerical Diffusion Problem
การแก้สมการนี้โดยตรงมักทำให้เกิด **Numerical Diffusion**:
- **เริ่มต้น:** รอยต่อคม (Step Function) จาก 1 → 0 ใน 1 Cell
- **ผ่านไป 10 ชั่วโมง:** รอยต่อเบลอ 0.9, 0.7, 0.5, 0.3, 0.1 (กิน 4-5 Cells)
- **หายนะ:** ผิวเบลอ → คำนวณ Surface Tension ไม่ได้ → น้ำดูระเหย

**Solution:** Interface Compression (บทถัดไป **[[02_Interface_Compression.md]]**)

---

## 4. Surface Tension

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain A: Physics & Fields** และ **Domain B: Numerics**
> - **File**: `constant/transportProperties` - กำหนดค่า `sigma`
> - **Keywords**: `sigma`, `surfaceTension`, `interfaceCompression`

VOF ใน OpenFOAM ใช้โมเดล **CSF (Continuum Surface Force)**:

$$ \mathbf{F}_{st} = \sigma \kappa \nabla \alpha $$

โดยที่:
- $\sigma$ (Sigma): สัมประสิทธิ์แรงตึงผิว (N/m) [Water-Air $\approx 0.07$]
- $\kappa$ (Kappa): ความโค้งของผิว คำนวณจาก:
  $$ \kappa = - \nabla \cdot \left( \frac{\nabla \alpha}{|\nabla \alpha|} \right) $$

> [!TIP] **ทำไมผิวเบลอแย่?**
> ถ้า $\alpha$ เบลอ → Gradient ไม่ชัน → Normal Vector $\mathbf{n}$ ไม่แม่นยำ → Curvature $\kappa$ ผิดเพี้ยน → เกิด **Spurious Currents** (กระแสปลอม) รอบฟองอากาศ

---

## 📊 Method Comparison: VOF vs Alternatives

| Feature | VOF (OpenFOAM) | Level Set | Eulerian-Eulerian |
| :--- | :--- | :--- | :--- |
| **ตัวแปรหลัก** | Volume Fraction ($\alpha$) | Distance Function ($\phi$) | $\alpha$ + 2 Velocity Fields |
| **Mass Conservation** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Fair (Mass loss possible) | ⭐⭐⭐⭐ Good |
| **Interface Sharpness** | ⭐⭐⭐ Good (with compression) | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐ Fair |
| **Topology Changes** | ⭐⭐⭐⭐⭐ Handles easily | ⭐⭐⭐⭐ Handles well | ⭐⭐⭐⭐⭐ Handles easily |
| **Computational Cost** | ⭐⭐⭐ Moderate | ⭐⭐⭐ Moderate | ⭐ High (2 velocity solvers) |
| **Curvature Accuracy** | ⭐⭐⭐ Good (if sharp) | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐ Fair |
| **งานที่เหมาะ** | Dam break, Tank sloshing, Wave impact | Droplet dynamics, Bubble shapes | Bubble columns, Sedimentation, Particle-laden flows |

**Key Insight:** OpenFOAM เลือก VOF เป็นหลักเพราะงานวิศวกรรมส่วนใหญ่ต้องการ **Mass Conservation** เป็นหลัก (มวลต้องหายไม่ได้) และต้องจัดการ Topology changes ที่รุนแรง (เช่น คลื่นแตก, ฟองแตก)

---

## 🎛️ Parameters Quick Reference

| Parameter | Location | Typical Value | Purpose |
| :--- | :--- | :--- | :--- |
| **cAlpha** | `system/fvSolution` | 0 - 1 (default: 1) | Interface compression coefficient |
| **maxCo** | `system/controlDict` | 0.2 - 0.5 | Maximum Courant number for stability |
| **nAlphaCorr** | `system/fvSolution` | 1 - 2 | Number of alpha corrector iterations |
| **nAlphaSubCycles** | `system/fvSolution` | 1 - 5 | Sub-cycling for sharp interface |
| **sigma** | `constant/transportProperties` | 0.07 (water-air) | Surface tension coefficient |
| **MULESCoeffs** | `system/fvSolution` | (varies) | Flux limiter settings for boundedness |

> [!TIP] **Quick Guidelines**
> - **Dam break / Sloshing**: `cAlpha: 1`, `maxCo: 0.3`, `nAlphaCorr: 1`
> - **Droplet dynamics**: `cAlpha: 0.5-1`, `maxCo: 0.2`, `nAlphaSubCycles: 2-3`
> - **Bubble columns**: `cAlpha: 1`, `maxCo: 0.4`, `nAlphaCorr: 2`

---

## 🧠 Concept Check

<details>
<summary><b>1. คำนวณความหนาแน่นผสม</b><br>ถ้า $\rho_{water} = 1000$ และ $\rho_{air} = 1$, ในเซลล์ที่มี $\alpha = 0.5$ ความหนาแน่นคือเท่าไหร่?</summary>

$\rho = 0.5(1000) + 0.5(1) = 500.5 \, kg/m^3$
</details>

<details>
<summary><b>2. ทำไม OpenFOAM ไม่ใช้ Level Set เป็นหลัก?</b></summary>

เพราะ OpenFOAM เน้นงานวิศวกรรมที่ "มวลต้องหายไม่ได้" (Conservation is key) วิธี Level Set แบบดั้งเดิมมักทำให้มวลหายเมื่อผ่านไปหลาย steps (ฟองเล็กลงเรื่อยๆ) ซึ่งยอมรับไม่ได้ในงานอุตสาหกรรม
</details>

<details>
<summary><b>3. VOF รู้ตำแหน่ง Interface ภายใน Cell หรือไม่?</b></summary>

**ไม่รู้** มันรู้แค่ "ปริมาณ" (Volume Fraction) เราต้องใช้เทคนิค Reconstruction เช่น Isosurface เพื่อสร้างภาพ Interface
</details>

<details>
<summary><b>4. ทำไม Density Ratio สูง (1000:1) ถึงเป็นปัญหา?</b></summary>

เพราะที่ Interface ความหนาแน่นจะกระโดดจาก 1 → 1000 ในระยะเพียง 1-2 Cells ทำให้ Pressure solver ต้องแก้สมการที่มีค่าสัมประสิทธิ์ที่แตกต่างกันมาก ซึ่งอาจทำให้เกิดปัญหาความเสถียร (Divergence) หากไม่มีการปรับแต่งที่เหมาะสม
</details>

---

## 🎓 How to Apply: Key Takeaways

### ✅ Core Concepts to Remember
1. **VOF = Raster Graphics**: ยอมสละความคมชัดเพื่อ Topology flexibility (การแตกรวมของฟอง/คลื่น)
2. **Density Jump is Critical**: อัตราส่วน 1000:1 ที่ Interface เป็นความท้าทายหลักของ Solver
3. **Sharp Interface = Everything**: Interface เบลอ → Surface Tension ผิด → Spurious Currents → การคำนวณล้มเหลว
4. **Mass Conservation is King**: นี่คือเหตุผลที่ OpenFOAM เลือก VOF ไม่ใช่ Level Set

### 🔧 Practical Application

#### Step 1: ตั้งค่าเริ่มต้นใน `0/alpha.water`
```cpp
dimensions      [0 0 0 0 0 0 0];

internalField   uniform 0;  // 0 = เต็มอากาศ, 1 = เต็มน้ำ

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1;  // น้ำไหลเข้า
    }
    
    walls
    {
        type            zeroGradient;  // ไม่มีการไหลผ่านผนัง
    }
}
```

#### Step 2: กำหนดคุณสมบัติใน `constant/transportProperties`
```cpp
phases (water air);

water
{
    transportModel  Newtonian;
    nu              nu [0 2 -1 0 0 0 0] 1e-06;
    rho             rho [1 -3 0 0 0 0 0] 1000;
}

air
{
    transportModel  Newtonian;
    nu              nu [0 2 -1 0 0 0 0] 1.48e-05;
    rho             rho [1 -3 0 0 0 0 0] 1;
}

sigma           sigma [0 2 -2 0 0 0 0] 0.07;  // Surface tension
```

#### Step 3: ปรับแต่ง Numerics ใน `system/fvSolution`
```cpp
solvers
{
    "alpha.water.*"
    {
        nAlphaCorr      1;
        nAlphaSubCycles 2;
        cAlpha          1;
        
        MULESCoeffs
        {
            // Flux limiter settings
        }
    }
}
```

### ⚠️ Common Pitfalls to Avoid

| Pitfall | Symptom | Solution |
| :--- | :--- | :--- |
| **ไม่กำหนดค่าเริ่มต้น α** | Solver ไม่รู้ว่ามีน้ำตรงไหน | ใช้ `setFields` หรือ `funkySetFields` สร้าง initial patch |
| **Mesh หยาบเกินไป** | Interface เบลอ, Curvature ผิด | ใช้ Refinement region บริเวณ interface |
| **maxCo สูงเกินไป** | Interface เบลอ, Solver diverge | ลด `maxCo` ให้อยู่ที่ 0.2-0.3 |
| **ไม่เข้าใจ Numerical Diffusion** | น้ำดูระเหยหายไปเรื่อยๆ | เปิด Interface Compression (`cAlpha > 0`) |
| **กำหนด BC ผิด** | น้ำไหลออก/เข้าผนัง | ใช้ `zeroGradient` ที่ผนัง ไม่ใช่ `fixedValue 0` |

---

## 📖 เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า**: [00_Overview.md](00_Overview.md)
- **บทถัดไป**: [02_Interface_Compression.md](02_Interface_Compression.md) - เรียนรู้วิธีรักษาความคมของ Interface ด้วย Interface Compression
- **บทเกี่ยวข้อง**: [03_Surface_Tension_Models.md](03_Surface_Tension_Models.md) - ทำความเข้าใจ CSF Model และ Spurious Currents อย่างละเอียด