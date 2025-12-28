# แนวคิดพื้นฐาน VOF (The VOF Concept)

> [!TIP] **ทำไมต้องเข้าใจ VOF?**
> การเข้าใจแนวคิด VOF เป็นสิ่งสำคัญมาก เพราะ:
> - **ความเสถียร**: การทำความเข้าใจการกระจายของ α จะช่วยให้คุณป้องกันปัญหาการแตกตัวของการคำนวณ (Divergence)
> - **ความแม่นยำ**: รู้จักกับ Interface Compression จะช่วยรักษาความคมของผิวน้ำให้เป็นธรรมชาติ
> - **ประสิทธิภาพ**: สามารถตั้งค่า Courant Number และ Time Step ได้อย่างเหมาะสม ทำให้การคำนวณเร็วและเสถียร

**Volume of Fluid (VOF)** เป็นหัวใจสำคัญของการจำลองการไหลแบบ Free Surface ใน OpenFOAM การทำความเข้าใจ "ปรัชญา" ของมันจะช่วยให้คุณปรับแต่งค่าต่างๆ ได้อย่างมีเหตุผล ไม่ใช่แค่จำสูตร

---

## 💡 แนวคิดเปรียบเทียบ: Raster vs. Vector (The Graphics Analogy)

> [!NOTE] **📂 OpenFOAM Context**
> แนวคิดนี้เป็นพื้นฐานของ **Domain A: Physics & Fields**
> - **File**: `0/alpha.water` - ไฟล์กำหนดค่าเริ่มต้นของ Phase Fraction
> - **Keywords**: `alpha.water`, `alpha1`, `volScalarField`
> - **Application**: เมื่อคุณเปิดไฟล์ `0/alpha.water` คุณจะเห็นค่า α ที่ถูกกำหนดให้กับแต่ละ Cell บน Mesh

ลองนึกภาพคุณกำลังวาดรูปวงกลมบนคอมพิวเตอร์ มีสองวิธีที่จะเก็บข้อมูลวงกลมนี้:

### 1. Vector (Lagrangian / Front Tracking)
- **วิธีเก็บ:** เก็บสมการของวงกลม ($x^2 + y^2 = r^2$) หรือเก็บจุดต่อกันเป็นเส้น
- **ข้อดี:** คมชัดกริบ ซูมแค่ไหนก็ไม่แตก
- **ข้อเสีย:** ถ้าวงกลมนี้แตกออกเป็น 2 วง หรือรวมร่างกับวงกลมอื่น สมการจะซับซ้อนมหาศาล (Topology Change is hard)

### 2. Raster / Pixel (Eulerian / VOF)
- **วิธีเก็บ:** แบ่งหน้าจอเป็นตาราง (Grid) แล้วระบายสีแต่ละช่อง
  - ช่องไหนอยู่ในวงกลม = สีดำ ($\alpha=1$)
  - ช่องไหนอยู่นอกวงกลม = สีขาว ($\alpha=0$)
  - ช่องที่ขอบตัดผ่าน = สีเทา ($0 < \alpha < 1$)
- **ข้อดี:** ไม่สนว่าจะมีกี่วง จะแตกจะรวมกันก็แค่เปลี่ยนสีในช่อง (Topology Chage is easy)
- **ข้อเสีย:** ภาพจะ "แตก" (Pixelated) หรือ "เบลอ" ถ้าตารางไม่ละเอียดพอ หรืออัลกอริทึมไม่ดี

> [!INFO] **VOF คือวิธี Raster**
> VOF ยอมสละความคมชัดระดับอนันต์ เพื่อแลกกับความสามารถในการจำลองการไหลที่ซับซ้อนและรุนแรง (เช่น คลื่นซัดฝั่ง) ได้อย่างทนทาน

---

## 1. ตัวแปร Phase Fraction ($\alpha$)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain A: Physics & Fields**
> - **File**: `0/alpha.water` - Field file สำหรับ Phase Fraction
> - **Keywords**: `internalField`, `boundaryField`, `fixedValue`, `zeroGradient`
> - **Practical Tip**: ค่า α ใน `internalField` ถูกกำหนดเป็นค่าคงที่ (uniform) หรือค่าแปรตามตำแหน่ง (non-uniform)

ใน OpenFOAM ตัวแปรพระเอกคือ `alpha.water` (หรือ `alpha1` ในเวอร์ชันเก่า):

$$ \alpha(\mathbf{x}, t) = \begin{cases} 1 & \text{ถ้าจุดนั้นมีน้ำเต็มๆ} \\ 0 & \text{ถ้าจุดนั้นมีแต่อากาศ} \\ 0 < \alpha < 1 & \text{ถ้าจุดนั้นมี interface} \end{cases} $$

### การตีความทางกายภาพใน Cell
ถ้า Cell หนึ่งมีปริมาตร $V$ และมีค่าน้ำ $\alpha = 0.4$:
- แปลว่ามีปริมาตรน้ำ $V_{water} = 0.4 \times V$
- มีปริมาตรอากาศ $V_{air} = 0.6 \times V$

> **Note:** VOF ไม่รู้ว่าน้ำลอยอยู่ "ตรงไหน" ใน Cell นั้น (มุมซ้าย? มุมขวา? ตรงกลาง?) มันรู้แค่ "ปริมาณ" รวม เราต้องใช้เทคนิค Reconstruction (เช่น Iso-surface) เพื่อเดาหน้าตาผิวหน้าเอาเอง

---

## 2. คุณสมบัติของ "ของไหลผสม" (The Mixture Fluid)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain A: Physics & Fields**
> - **File**: `constant/transportProperties` - ไฟล์กำหนดคุณสมบัติทางกายภาพของของไหลแต่ละเฟส
> - **Keywords**: `phases`, `transportModel`, `nu`, `rho`
> - **Critical Point**: ค่า Density Ratio (อัตราส่วนความหนาแน่น) สูงมาก (1000:1) ส่งผลต่อความเสถียรของ Pressure Solver

VOF ไม่ได้แก้สมการ Navier-Stokes สองรอบ (สำหรับน้ำและอากาศ) แต่แก้รอบเดียวสำหรับ **"ของไหลผสมเสมือน (Effective Fluid)"**:

### ความหนาแน่น (Density)
$$ \rho = \alpha \rho_{water} + (1-\alpha) \rho_{air} $$

### ความหนืด (Dynamic Viscosity)
$$ \mu = \alpha \mu_{water} + (1-\alpha) \mu_{air} $$

> [!WARNING] **The Density Jump Challenge**
> สำหรับน้ำและอากาศ, $\rho_{water} \approx 1000$ และ $\rho_{air} \approx 1$
> ที่รอยต่อ (Interface), ความหนาแน่นจะกระโดดถึง **1000 เท่า** ในระยะห่างแค่ 1-2 Grid cells
> นี่คือสาเหตุที่ Solver VOF ต้องมีความเสถียรสูงมาก ไม่งั้นสมการ Pressure จะระเบิด (Diverge) ทันที

---

## 3. สมการหลัก: The Transport Equation

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain B: Numerics & Linear Algebra**
> - **File**: `system/fvSchemes` - ไฟล์กำหนดรูปแบบการ Discretization
> - **Keywords**: `divSchemes`, `Gauss`, `upwind`, `MULES`, `limited`
> - **Key Insight**: การเลือก Scheme สำหรับ `div(phi,alpha)` มีผลต่อ Numerical Diffusion และความคมของ Interface

รอยต่อเคลื่อนที่ไปตามการไหลของของไหล ($\mathbf{U}$) ตามสมการ Advection มาตรฐาน:

$$ \frac{\partial \alpha}{\partial t} + \nabla \cdot (\mathbf{U} \alpha) = 0 $$

### ปัญหาของการใช้สมการนี้ตรงๆ
ในการคำนวณเชิงตัวเลข (Numerics) การแก้สมการนี้มักจะทำให้เกิดปัญหา **Numerical Diffusion** (การแพร่):
- **เริ่มต้น:** รอยต่อคมกริบ (Step Function) จาก 1 ไป 0 ใน 1 Cell
- **ผ่านไป 10 Time steps:** รอยต่อเริ่มเบลอ ไล่ระดับ 0.9, 0.7, 0.5, 0.3, 0.1 กินพื้นที่ 4-5 Cells
- **หายนะ:** เมื่อผิวเบลอ เราจะคำนวณแรงตึงผิว (Surface Tension) ไม่ได้ และน้ำจะดูเหมือนระเหยหายไป

**วิธีแก้ของ OpenFOAM:** การใช้เทอมอัด (Compression Term) ในบทต่อไป **[[02_Interface_Compression]]**

---

## 4. แรงตึงผิว (Surface Tension)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain A: Physics & Fields** และ **Domain B: Numerics**
> - **File**: `constant/transportProperties` - กำหนดค่า `sigma` (ค่าสัมประสิทธิ์แรงตึงผิว)
> - **Keywords**: `sigma`, `surfaceTension`, `interfaceCompression`
> - **Numerics**: ความแม่นยำของการคำนวณ Curvature ($\kappa$) ขึ้นกับความละเอียดของ Mesh และ Gradient Scheme ใน `fvSchemes`

VOF ใน OpenFOAM ใช้โมเดล **CSF (Continuum Surface Force)** โดยแปลงแรงตึงผิวให้เป็นแรงกระทำต่อปริมาตร ($\mathbf{F}_{st}$):

$$ \mathbf{F}_{st} = \sigma \kappa \nabla \alpha $$

โดยที่:
- $\sigma$ (Sigma): สัมประสิทธิ์แรงตึงผิว (N/m) [Water-Air $\approx 0.07$]
- $\kappa$ (Kappa): ความโค้งของผิว (Curvature) คำนวณจาก $\alpha$:
  $$ \kappa = - \nabla \cdot \left( \frac{\nabla \alpha}{|\nabla \alpha|} \right) $$

> [!TIP] **ทำไมผิวเบลอถึงแย่?**
> ถ้า $\alpha$ เบลอ (เกรเดียนต์ไม่ชัน), การคำนวณ $\mathbf{n} = \frac{\nabla \alpha}{|\nabla \alpha|}$ จะไม่แม่นยำ ทำให้ค่าความโค้ง $\kappa$ ผิดเพี้ยน ส่งผลให้เกิด **Spurious Currents** (กระแสน้ำวนปลอมๆ) รอบๆ ฟองอากาศที่อยู่นิ่งๆ

---

## 📊 เปรียบเทียบ VOF กับวิธีอื่น

| Feature | VOF (OpenFOAM) | Level Set | Eulerian-Eulerian |
| :--- | :--- | :--- | :--- |
| **ตัวแปรหลัก** | Volume Fraction ($\alpha$) | Distance Function ($\phi$) | $\alpha$ + 2 Velocity Fields |
| **จุดเด่น** | รักษามวลดีเยี่ยม (Mass Conservation) | ผิวเรียบเนียน คำนวณ Curvature แม่น | แยก Velocity ของแต่ละเฟสได้ (Slip velocity) |
| **จุดด้อย** | ผิวอาจเบลอ (Numerical Smearing) | มวลหายนิรภัย (Mass Loss) | เปลืองทรัพยากรคำนวณมาก |
| **งานที่เหมาะ** | Dam break, Tank Sloshing | Droplet dynamics, precision flows | Bubble columns, Sedimentation |

---

## 🧠 Concept Check: ทดสอบความเข้าใจ

1.  **ถ้า $\rho_{water} = 1000$ และ $\rho_{air} = 1$, ในเซลล์ที่มี $\alpha = 0.5$ ความหนาแน่นของเซลล์นั้นคือเท่าไหร่?**
    <details>
    <summary>เฉลย</summary>
    $\rho = 0.5(1000) + 0.5(1) = 500.5 \, kg/m^3$
    </details>

2.  **ทำไม OpenFOAM ถึงไม่ใช้ Level Set Method เป็นวิธีหลัก?**
    <details>
    <summary>เฉลย</summary>
    เพราะ OpenFOAM เน้นงานวิศวกรรมที่ "มวลต้องหายไม่ได้" (Conservation is key) วิธี Level Set แบบดั้งเดิมมักทำมวลหายเมื่อผ่านไปหลาย steps (ฟองอากาศเล็กลงเรื่อยๆ) ซึ่งยอมรับไม่ได้ในงานอุตสาหกรรม
    </details>

3.  **VOF รู้ตำแหน่งของ Interface ภายใน Cell หรือไม่?**
    <details>
    <summary>เฉลย</summary>
    **ไม่รู้** มันรู้แค่ "ปริมาณ" (Volume Fraction) เราต้องใช้เทคนิค Reconstruction เช่น Isosurface หรือ Geometric Reconstruction เพื่อสร้างภาพ Interface ขึ้นมา
    </details>

---

## 📖 เอกสารที่เกี่ยวข้อง

*   **บทก่อนหน้า**: [00_Overview.md](00_Overview.md)
*   **บทถัดไป**: [02_Interface_Compression.md](02_Interface_Compression.md)