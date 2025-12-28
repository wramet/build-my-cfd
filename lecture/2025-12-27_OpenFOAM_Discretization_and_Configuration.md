# บันทึกบทเรียน: พื้นฐาน OpenFOAM - Discretization, การตั้งค่า และโครงสร้างโค้ด
**วันที่:** 27 ธันวาคม 2025
**หัวข้อ:** จากแคลคูลัสสู่โค้ด: เข้าใจกลไกการทำงานหลักของ OpenFOAM

> [!TIP] ทำไมต้องเข้าใจ Discretization?
> การ Discretization คือการแปลงสมการฟิสิกส์ที่เป็น **Continuous (คณิตศาสตร์ต่อเนื่อง)** ให้กลายเป็น **Discrete (พีชคณิตลับๆ)** ที่คอมพิวเตอร์คำนวณได้ การเลือก Scheme ที่เหมาะสมจะส่งผลโดยตรงต่อ:
> - **ความเสถียร (Stability):** จำลองได้โดยไม่ระเบิด
> - **ความแม่นยำ (Accuracy):** ผลลัพธ์ใกล้ความจริง
> - **ประสิทธิภาพ (Efficiency):** คำนวณเสร็จไว
>
> **ความสำคัญต่อการจำลอง:** การตั้งค่า `system/fvSchemes` และ `system/fvSolution` ที่ผิดพลาดอาจทำให้ **Simulation ระเบิด (Blow up)** แม้ว่าจะตั้ง Boundary Conditions ถูกต้องก็ตาม

---

## 1. บทนำ: ภาพรวม (The Big Picture)
ในบทเรียนนี้ เราได้สำรวจวิธีการที่ OpenFOAM แปลงโจทย์ฟิสิกส์ของการไหลที่ซับซ้อนให้กลายเป็นสิ่งที่คอมพิวเตอร์คำนวณได้ โดยแบ่งหน้าที่ออกเป็น 4 ส่วนหลัก:
1.  **นักแปลภาษา (`fvSchemes`):** แปลงสมการแคลคูลัสให้เป็นสมการพีชคณิต
2.  **นักวางแผน (`fvSolution`):** วางแผนวิธีการแก้สมการพีชคณิตที่ได้มา
3.  **โครงสร้างโค้ด (`createFields.H`):** วิธีการประกาศตัวแปรและจองพื้นที่ในหน่วยความจำ (C++)
4.  **การวิเคราะห์ผล (`functionObjects`):** การแปลงข้อมูลดิบให้เป็นค่าทางวิศวกรรมที่มีความหมาย

---

## 1.5 รากฐานทางฟิสิกส์: 3 สมการควบคุม (The 3 Governing Equations)

> [!NOTE] **📂 OpenFOAM Context**
> **ไฟล์ที่เกี่ยวข้อง:**
> - **`0/U`** — ค่าเริ่มต้นและ Boundary Condition ของความเร็ว (Velocity)
> - **`0/p`** — ค่าเริ่มต้นและ Boundary Condition ของความดัน (Pressure)
> - **`constant/transportProperties`** — คุณสมบัติของไหล (ความหนืด `nu`, ความหนาแน่น `rho`)
> - **`constant/turbulenceProperties`** — ตั้งค่า Turbulence Model (k-ε, k-ω, ฯลฯ)
>
> **คำสำคัญ (Keywords):**
> - `nu` (Kinematic Viscosity), `rho` (Density), `mu` (Dynamic Viscosity)
> - `RASModel`, `LESModel`, `laminar`
> - `boundaryField`, `fixedValue`, `zeroGradient`

ก่อนจะไปถึงการ Discretize เราต้องเข้าใจ **"โจทย์ฟิสิกส์"** ที่ OpenFOAM ต้องแก้ก่อน โดยแบ่งออกเป็น 3 ภารกิจหลัก:

### ภารกิจที่ 1: การอนุรักษ์มวล (Continuity Equation)

#### Step-by-Step: จากความจริงสู่สมการ
1.  **Step 1: ความจริงทางฟิสิกส์ (Physics)**
    "ของไหลหายไปไหนไม่ได้ และเกิดขึ้นเองไม่ได้" (Mass In = Mass Out + Accumulation)
2.  **Step 2: คณิตศาสตร์ (Math)**
    $$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$$
    *   *กรณี Incompressible:* $\nabla \cdot \mathbf{u} = 0$ (ปริมาตรคงที่ตลอดเวลา)
3.  **Step 3: โค้ด OpenFOAM (Code)**
    ```cpp
    fvc::div(phi)  // คำนวณ Flux รวมที่ไหลออกจากเซลล์ (ควรเป็น 0)
    ```
4.  **Step 4: ความหมายใน Simulation (Insight)**
    เราไม่ได้แก้สมการนี้เพื่อหา "มวล" แต่ใช้เป็น **เงื่อนไขบังคับ (Constraint)** เพื่อสร้างสมการความดัน (Pressure Equation)

---

### ภารกิจที่ 2: การอนุรักษ์โมเมนตัม (Navier-Stokes Equation)

#### Step-by-Step: กฎของนิวตันในของไหล
1.  **Step 1: ความจริงทางฟิสิกส์ (Physics)**
    $F = ma$ (แรง = มวล $\times$ ความเร่ง)
2.  **Step 2: คณิตศาสตร์ (Math)**
    $$\underbrace{\frac{\partial (\rho \mathbf{u})}{\partial t} + \nabla \cdot (\rho \mathbf{u} \mathbf{u})}_{\text{ความเร่ง (เปลี่ยนตามเวลา + เคลื่อนที่)}} = \underbrace{-\nabla p}_{\text{แรงดัน}} + \underbrace{\mu \nabla^2 \mathbf{u}}_{\text{แรงหนืด}} + \mathbf{f}$$
3.  **Step 3: โค้ด OpenFOAM (Code)**
    ```cpp
    fvVectorMatrix UEqn
    (
        fvm::ddt(rho, U)                // ความเร่ง (เวลา)
      + fvm::div(phi, U)                // ความเร่ง (การพา - Convection)
      - fvm::laplacian(mu, U)           // แรงหนืด (Diffusion)
     ==
       -fvc::grad(p)                    // แรงดัน (Source Term)
    );
    ```
4.  **Step 4: ความยาก (Challenge)**
    เทอม Convection ($\nabla \cdot \mathbf{u}\mathbf{u}$) ทำให้สมการเป็น **Non-linear** (ความเร็วคูณความเร็ว) ทำให้แก้ยากและต้องวน Loop

---

### ภารกิจที่ 3: การอนุรักษ์พลังงาน (Energy Equation)

#### Step-by-Step: ความร้อนและอุณหภูมิ
1.  **Step 1: ความจริงทางฟิสิกส์ (Physics)**
    "พลังงานไม่สูญหาย แต่เปลี่ยนรูปได้" (First Law of Thermodynamics)
2.  **Step 2: คณิตศาสตร์ (Math)**
    $$\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{u} h) = k \nabla^2 T + \text{Source}$$
3.  **Step 3: โค้ด OpenFOAM (Code)**
    ```cpp
    fvScalarMatrix EEqn
    (
        fvm::ddt(rho, h) + fvm::div(phi, h)  // การพาความร้อน
      - fvm::laplacian(alphaEff, h)          // การนำความร้อน
    );
    ```
4.  **Step 4: เมื่อไหร่ต้องใช้? (Usage)**
    *   ❌ **น้ำไหลในท่อปกติ:** ไม่ต้องใช้ (Isothermal)
    *   ✅ **อากาศอัดตัวได้ (Compressible):** ต้องใช้ เพราะความหนาแน่น $\rho$ เปลี่ยนตาม $T$
    *   ✅ **Heat Transfer:** ต้องใช้ เพื่อดูการกระจายอุณหภูมิ

---

### 🔢 เลขไร้มิติ: ตัวบ่งชี้ Flow Regime

เพื่อรู้ว่าควรใช้ Solver หรือ Model ไหน เราต้องคำนวณ **เลขไร้มิติ** 2 ตัวหลัก:

#### 1. Reynolds Number ($Re$) — บอก Laminar vs Turbulent
$$Re = \frac{\rho U L}{\mu} = \frac{U L}{\nu}$$

- **$Re < 2300$ (ในท่อ):** Laminar flow — เรียบ ลู่ เป็นชั้นๆ
- **$Re > 4000$ (ในท่อ):** Turbulent flow — ปั่นป่วน มี eddy สุ่มเป็นมิติ
- **2300 < Re < 4000:** Transition region — อาจเป็นทั้งสองแบบ

**ผลต่อ OpenFOAM:**
- ถ้า $Re$ ต่ำ (Laminar): ใช้ `icoFoam` (incompressible laminar)
- ถ้า $Re$ สูง (Turbulent): ต้องใช้ **Turbulence Model** (k-ε, k-ω SST, Spalart-Allmaras) เช่น `simpleFoam` + `RASModel kEpsilon`

#### 2. Mach Number ($Ma$) — บอก Compressible vs Incompressible
$$Ma = \frac{U}{c} = \frac{\text{Flow Velocity}}{\text{Speed of Sound}}$$

- **$Ma < 0.3$:** Incompressible flow — ความหนาแน่นคงที่ (ใช้ `simpleFoam`, `pimpleFoam`)
- **$0.3 < Ma < 0.8$:** Subsonic compressible — ต้องคำนึงถึงการอัดตัว (ใช้ `rhoSimpleFoam`, `rhoPimpleFoam`)
- **$Ma > 0.8$:** Transonic/Supersonic — มี shock waves (ใช้ `sonicFoam`, `rhoCentralFoam`)

**ผลต่อ Equation of State:**
- Incompressible ($Ma < 0.3$): $\rho = \text{constant}$ (หรือ $\rho = \rho(T)$ สำหรับ Boussinesq)
- Compressible ($Ma > 0.3$): $p = \rho R T$ (Ideal Gas Law)

> [!tip] Practical Tip
> ก่อนเริ่ม Simulation เสมอ คำนวณ $Re$ และ $Ma$ เพื่อ:
> 1. เลือก Solver ที่เหมาะสม
> 2. ตัดสินใจว่าต้องใช้ Turbulence model ไหม
> 3. ตั้งค่า Boundary conditions อย่างถูกต้อง

---

### 📊 Summary: สมการ → Code Mapping

| สมการ | ฟิสิกส์ | OpenFOAM Code | เมื่อไหร่ใช้ |
|--------|---------|---------------|--------------|
| **Continuity** | $\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$ | `fvc::div(phi)`, `fvm::ddt(rho)` | ทุก Solver (implicit ใน pressure-velocity coupling) |
| **Momentum** | $\frac{D\mathbf{u}}{Dt} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$ | `fvm::ddt(rho,U) + fvm::div(phi,U) + turbulence->divDevRhoReff(U)` | ทุก Solver (หลัก) |
| **Energy** | $\rho c_p \frac{DT}{Dt} = k \nabla^2 T + \Phi$ | `fvm::div(phi,h) + fvm::laplacian(alphaEff,h)` | Heat transfer หรือ Compressible flow |

---

## 2. นักแปลภาษา: `system/fvSchemes`

> [!NOTE] **📂 OpenFOAM Context**
> **ไฟล์:** **`system/fvSchemes`**
>
> **บทบาท:** แปลงสมการแคลคูลัส (Continuous) → สมการพีชคณิต (Discrete)
>
> **คำสำคัญ (Keywords) ในไฟล์:**
> - **`ddtSchemes`** — การ Discretize เทอมเวลา $\frac{\partial}{\partial t}$
>   - `Euler` (1st order), `backward` (2nd order), `CrankNicolson` (2nd order)
> - **`gradSchemes`** — การคำนวณ Gradient $\nabla \phi$
>   - `Gauss linear` (มาตรฐาน), `leastSquares` (แม่นกว่าแต่แพง)
> - **`divSchemes`** — การ Discretize เทอม Divergence $\nabla \cdot (\dots)$ (สำคัญที่สุด!)
>   - `Gauss linear` (แม่นยำ), `Gauss upwind` (เสถียร), `limitedLinear` (สมดุล)
> - **`laplacianSchemes`** — การ Discretize เทอม Laplacian $\nabla \cdot (\Gamma \nabla \phi)$
>   - `Gauss linear corrected` (มาตรฐาน), `Gauss linear limited` (mesh เบี้ยวหนัก)
> - **`interpolationSchemes`** — การ Interpolate ค่าจาก Cell Center ไปหน้าเซลล์
>   - `linear` (เฉลี่ยเส้นตรง)
> - **`snGradSchemes`** — ความชันปกติที่ผิวหน้า $\nabla \phi \cdot \mathbf{n}$
>   - `corrected` (แก้ non-orthogonality)
>
> **ผลต่อการจำลอง:**
> - ผิด → **ระเบิด (Blow up)** หรือ **ผลลัพธ์เบลอ (Numerical Diffusion)**
> - ถูก → **สมดุลระหว่างความแม่นยำและความเสถียร**

ไฟล์นี้รับผิดชอบเรื่อง **Discretization** โดยเปลี่ยนโจทย์จาก **Continuous (Calculus)** ให้เป็น **Discrete (Algebra)** ผ่านกระบวนการเป็นขั้นเป็นตอนดังนี้:

### Step-by-Step: กลไกการทำงานของ Schemes

#### 1. เป้าหมาย (The Goal)
เราต้องการเปลี่ยนเทอมในสมการอนุพันธ์ (เช่น $\nabla \cdot (\rho \mathbf{u})$) ให้เป็นผลรวมของค่าต่างๆ บนตารางกริด เพื่อสร้างสมการ $Ax=b$

#### 2. ปัญหา (The Problem)
ตามทฤษฎี **Finite Volume Method (FVM)** การคำนวณเทอมต่างๆ ต้องทำที่ **"ผิวหน้าเซลล์ (Face)"** (ตาม Gauss's Theorem):
$$ \int_V \nabla \cdot (\rho \mathbf{u}) dV = \sum_f (\mathbf{u} \rho)_f \cdot \mathbf{S}_f $$
*แต่!!!* OpenFOAM เก็บค่าตัวแปร (เช่น $p, U, T$) ไว้ที่ **"จุดกึ่งกลางเซลล์ (Cell Center, $P$)"** เท่านั้น

#### 3. ทางออก (The Solution)
เราต้อง **"ประมาณค่า (Interpolate)"** จากจุดกึ่งกลาง ($P$) ไปยังผิวหน้า ($f$) วิธีการประมาณค่านี้แหละคือสิ่งที่เราเรียกว่า **"Schemes"**

---

### 2.1 `divSchemes` (Divergence / Convection)

> [!NOTE] **📂 OpenFOAM Context**
> **ไฟล์:** **`system/fvSchemes`**
> **Section:** `divSchemes`
>
> **ตัวอย่างการตั้งค่า:**
> ```cpp
> divSchemes
> {
>     default         none;
>     div(phi,U)      Gauss upwind;              // สำหรับความเร็ว (เสถียร)
>     div(phi,k)      Gauss limitedLinear 1;     // สำหรับ turbulent kinetic energy
>     div(phi,epsilon) Gauss limitedLinear 1;    // สำหรับ epsilon dissipation
>     div((nuEff*dev2(T(grad(U))))) Gauss linear corrected; // สำหรับ diffusion
> }
> ```
>
> **คำสำคัญ (Keywords):**
> - `Gauss upwind` — เสถียรสุด แต่เบลอ (Numerical Diffusion สูง)
> - `Gauss linear` — แม่นยำ (2nd order) แต่อาจระเบิดถ้า flow รุนแรง
> - `Gauss linearUpwind` — สมดุลระหว่างแม่นยำและเสถียร
> - `limitedLinear <φ>` — จำกัดค่าเพื่อความเสถียร (<φ> คือ limiter factor 0-1)
>
> **ผลกระทบ:**
> - ใช้ `linear` กับ flow รุนแรง → **ระเบิด (Oscillations)**
> - ใช้ `upwind` ตลอด → **ผลลัพธ์เบลอ (False Diffusion)**
>
> **Best Practice:** เริ่มต้นด้วย `upwind` จนเสถียร แล้วค่อยเปลี่ยนเป็น `limitedLinear` เพื่อความแม่นยำ

**โจทย์:** เทอมการพา $\nabla \cdot (\rho \mathbf{u})$ — ข้อมูลไหลไปตามลม
*   **Step 1: พิจารณาทิศทางไหล** ข้อมูลควรไหลจากต้นน้ำ (Upwind) ไปปลายน้า
*   **Step 2: เลือกวิธีการเดาค่า (Interpolation Scheme)**
    *   **Option A: `Gauss linear` (Central Differencing)**
        *   *วิธีคิด:* เอาค่า 2 ฝั่งมาเฉลี่ยกันตรงๆ
        *   *ผลลัพธ์:* แม่นยำสูง (2nd order) แต่ถ้าลมแรง ค่าอาจกระโดด (Unbounded) จนระเบิดได้
    *   **Option B: `Gauss upwind`**
        *   *วิธีคิด:* เอาค่าจากฝั่ง "ต้นลม" มาใช้เลย
        *   *ผลลัพธ์:* เสถียรสุดๆ (Bounded) แต่ค่าจะเบลอๆ (Numerical Diffusion) เหมือนภาพไม่ชัด
    *   **Option C: `Gauss linearUpwind` / `limitedLinear` (แนะนำ)**
        *   *วิธีคิด:* ลูกผสม พยายามใช้ Linear ให้แม่น แต่ถ้าเริ่มแกว่งจะถอยมาใช้ Upwind
        *   *ผลลัพธ์:* สมดุลระหว่างความแม่นและความเสถียร

### 2.2 `laplacianSchemes` (Laplacian / Diffusion)

> [!NOTE] **📂 OpenFOAM Context**
> **ไฟล์:** **`system/fvSchemes`**
> **Section:** `laplacianSchemes`
>
> **ตัวอย่างการตั้งค่า:**
> ```cpp
> laplacianSchemes
> {
>     default         Gauss linear corrected;
>     laplacian(nu,U)  Gauss linear corrected;     // สำหรับ momentum diffusion
>     laplacian((1|A(U)),p)  Gauss linear corrected; // สำหรับ pressure equation
>     laplacian(alphaEff,h) Gauss linear corrected; // สำหรับ energy equation
> }
> ```
>
> **คำสำคัญ (Keywords):**
> - `Gauss linear uncorrected` — เร็วที่สุด ใช้กับ mesh สี่เหลี่ยมเท่านั้น (Orthogonal)
> - `Gauss linear corrected` — มาตรฐาน แก้ non-orthogonality (สำหรับ mesh ทั่วไป)
> - `Gauss linear limited <φ>` — ใช้กับ mesh เบี้ยวหนักมาก (> 70°) (<φ> = 0.33-0.5)
>
> **ผลกระทบของ Non-orthogonality:**
> - Mesh เบี้ยว (< 70°) → ใช้ `corrected` (แม่นยำ)
> - Mesh เบี้ยวหนัก (> 70°) → ใช้ `limited` หรือเพิ่ม `nNonOrthogonalCorrectors` ใน `fvSolution`
>
> **เช็ค Mesh:** รัน `checkMesh` เพื่อดูค่า `max non-orthogonality`

**โจทย์:** เทอมการแพร่ $\nabla \cdot (\Gamma \nabla \phi)$ — เกี่ยวข้องกับความชัน (Gradient)
*   **Step 1: คำนวณความชันที่ผิวหน้า** เราต้องหา $\nabla \phi \cdot \mathbf{n}$
*   **Step 2: ตรวจสอบคุณภาพ Mesh (Orthogonality)**
    *   *Mesh สวย:* เส้นเชื่อมเซลล์ ($\mathbf{d}$) ตั้งฉากกับผิวหน้า ($\mathbf{n}$) → คำนวณง่าย
    *   *Mesh เบี้ยว:* เส้นไม่ตั้งฉาก → คำนวณตรงๆ จะผิด ต้องมีเทอมแก้ (Correction)
*   **Step 3: เลือกวิธีการแก้ (Correction Scheme)**
    *   **Option A: `Gauss linear uncorrected`**
        *   *ใช้เมื่อ:* Mesh เป็นสี่เหลี่ยมเป๊ะ (Orthogonal) เท่านั้น เร็วที่สุด
    *   **Option B: `Gauss linear corrected` (Standard)**
        *   *ใช้เมื่อ:* Mesh ทั่วไป มีความเบี้ยวบ้าง (Non-orthogonal) แม่นยำ แต่คำนวณเยอะกว่า
    *   **Option C: `Gauss linear limited`**
        *   *ใช้เมื่อ:* Mesh เบี้ยวหนักมาก (> 70-80 องศา) แก้เต็มสูบแล้วระเบิด ต้องแก้แบบยั้งๆ (Limited) เพื่อความอยู่รอด

---

### 2.3 รายละเอียดเชิงลึก: การแก้ปัญหา Mesh เบี้ยว (Non-Orthogonality Correction)

**ปัญหา (The Issue):** ในโลกความเป็นจริง Mesh ไม่ได้สวยงามเป็นสี่เหลี่ยมผืนผ้าเสมอไป เส้นที่ลากเชื่อมระหว่างจุดกึ่งกลางเซลล์ ($\mathbf{d}$) มักจะไม่ตั้งฉากกับผิวหน้าสัมผัส ($\mathbf{n}$)

**ผลกระทบ:** การคำนวณ Gradient ($\nabla \phi$) แบบปกติจะผิดพลาด เพราะทิศทางมันเพี้ยน

#### Step-by-Step: วิธีการคำนวณและแก้ไข

1.  **Step 1: แบ่งส่วน Gradient**
    OpenFOAM จะแยก Gradient ที่ผิวหน้าออกเป็น 2 ส่วน:
    $$\nabla \phi_f \cdot \mathbf{n} = \underbrace{\frac{\phi_N - \phi_P}{|\mathbf{d}|}}_{\text{Orthogonal part (A)}} + \underbrace{\text{Correction term}}_{\text{Non-orthogonal part (B)}}$$

2.  **Step 2: คำนวณส่วนตรง (A)**
    คำนวณเหมือน Mesh ปกติ (คิดว่ามันตั้งฉาก) — *ส่วนนี้ทำได้ง่ายและเร็ว*

3.  **Step 3: คำนวณส่วนแก้ (B)**
    ส่วนนี้ซับซ้อนและต้องเลือกวิธีจัดการ:
    *   **แบบ Uncorrected:** ทิ้งส่วน B ไปเลย (สมมติว่า A ถูกแล้ว) → *เร็วแต่ผิด*
    *   **แบบ Corrected:** คำนวณ B แล้วเอาไปบวกเพิ่ม → *แม่นแต่ต้องวนลูปทำซ้ำ*
    *   **แบบ Limited:** คำนวณ B แต่เอามาใช้แค่บางส่วน (Limit) ไม่ให้ค่ากระโดด → *ปลอดภัยไว้ก่อน*

> [!tip] Practical Tip
> **Workflow ที่แนะนำ:**
> 1.  เริ่มด้วย `corrected` เสมอ (มาตรฐาน)
> 2.  ถ้า Simulation ระเบิด ให้เช็ค `checkMesh`
> 3.  ถ้า Non-orthogonality > 70° ให้เปลี่ยนไปใช้ `limited 0.5` หรือ `limited 0.33`

---

### 2.4 Flux Field (`phi`) — หัวใจของ FVM

**คำถาม:** ทำไม OpenFOAM ถึงขาด `phi` ไม่ได้?

#### Step-by-Step: ความสำคัญของ `phi`

1.  **Step 1: ธรรมชาติของการไหล (Physics)**
    การไหลคือการเคลื่อนที่ผ่าน "ผิวหน้า (Face)" ของปริมาตรควบคุม

2.  **Step 2: การสร้างตัวแปร (Data Structure)**
    OpenFOAM สร้างตัวแปรพิเศษชื่อ `phi` (Surface Scalar Field) เก็บค่า **Mass Flux** ($\dot{m} = \rho \mathbf{u} \cdot \mathbf{S}_f$) ที่ผิวหน้าทุกผิว
    *   หน่วย: $[kg/s]$ หรือ $[m^3/s]$ (ถ้า Incompressible)

3.  **Step 3: การใช้งาน (Usage)**
    *   **ใช้คำนวณการพา (Convection):** ทุกสมการที่ของไหลพาอะไรไปด้วย (ความร้อน, โมเมนตัม) จะใช้ `phi` ในการคำนวณ `fvm::div(phi, ...)`
    *   **ใช้รักษา Balance:** Solver จะบังคับให้ผลรวม `phi` เข้า-ออกเซลล์เป็น 0 (Continuity) เพื่อให้มวลไม่หาย

---

### 2.5 การเลือกเครื่องมือ: `fvm` vs `fvc`

> [!NOTE] **📂 OpenFOAM Context**
> **ไฟล์:** **Solver Source Code** (เช่น `simpleFoam.C`, `icoFoam.C`)
> **ตำแหน่ง:** ในฟังก์ชัน main() หรือ within time loop
>
> **คำสำคัญ (Keywords):**
> - **`fvm::`** (Finite Volume Method) — สร้าง Matrix ($A$) สำหรับ Implicit
> - **`fvc::`** (Finite Volume Calculus) — คำนวณ Source Term ($b$) สำหรับ Explicit
>
> **ตัวอย่างการใช้งานใน Solver:**
> ```cpp
> // ใน solver code (เช่น simpleFoam.C)
> fvVectorMatrix UEqn
> (
>     fvm::ddt(U)                          // Matrix (Implicit)
>   + fvm::div(phi, U)                     // Matrix (Implicit)
>   - fvm::laplacian(nu, U)                // Matrix (Implicit)
> );
>
> solve(UEqn == -fvc::grad(p));            // Explicit pressure gradient
> ```
>
> **กฎสำคัญ:**
> - ตัวแปรที่ต้องการหาค่า (Unknown) → ใช้ `fvm::`
> - ตัวแปรที่รู้ค่าแล้ว (Known) → ใช้ `fvc::`
>
> **ผลกระทบ:**
> - ใช้ `fvc` กับ Unknown → **Explicit** (เร็วแต่ไม่เสถียร ต้องใช้ Δt เล็กๆ)
> - ใช้ `fvm` กับ Known → **Implicit** (เสถียรแต่เสียเวลา compile)
>
> **Memory Trick:** M = Matrix, C = Calculus

นี่คือจุดตัดสินใจที่สำคัญที่สุดในการเขียน Code: **จะใช้อันไหนเมื่อไหร่?**

#### Step-by-Step: กระบวนการตัดสินใจ

1.  **Step 1: ดูตัวแปรที่ต้องการหา (Identify Unknown)**
    สมมติเรากำลังแก้สมการหาค่า $U$ (ความเร็ว) ณ เวลาปัจจุบัน
    *   $U$ คือ **Unknown**
    *   ค่าอื่นๆ ($p$, $U_{old}$) คือ **Known**

2.  **Step 2: เลือกเครื่องมือ (Select Operator)**

    *   **ทางเลือก A: `fvm::` (Finite Volume Method) — สำหรับ Unknown**
        *   *หน้าที่:* สร้าง **Matrix Coefficient** ($A$)
        *   *กลไก:* มันจะบอกว่า "ค่าของฉันขึ้นอยู่กับเพื่อนบ้านนะ" แล้วเขียนลงใน Matrix
        *   *ผลลัพธ์:* Implicit (เสถียรมาก)
        *   *ใช้เมื่อ:* เทอมนั้นมีตัวแปรที่เรากำลังหาค่า (เช่น `fvm::div(phi, U)` ในสมการ $U$)

    *   **ทางเลือก B: `fvc::` (Finite Volume Calculus) — สำหรับ Known**
        *   *หน้าที่:* คำนวณออกมาเป็น **ตัวเลข (Source Term)** ($b$)
        *   *กลไก:* เอาค่าที่มีอยู่แล้วมาบวกลบคูณหารกันเลย
        *   *ผลลัพธ์:* Explicit (เร็วแต่ต้องระวัง)
        *   *ใช้เมื่อ:* เทอมนั้นรู้ค่าหมดแล้ว หรือต้องการย้ายไปฝั่งขวาของสมการ (เช่น `fvc::grad(p)`)

3.  **Step 3: ประกอบร่าง (Assembly)**
    ```cpp
    solve
    (
        fvm::ddt(rho, U)        // Unknown (Matrix)
      + fvm::div(phi, U)        // Unknown (Matrix)
      ==
      - fvc::grad(p)            // Known (Vector b)
    );
    ```

> [!hint] Memory Trick
> *   **M** in fv**M** = **M**atrix (สร้างเมทริกซ์ รอแก้)
> *   **C** in fv**C** = **C**alculus (คิดเลขเลย เสร็จจบ)

---

## 3. นักวางแผน: `system/fvSolution`

> [!NOTE] **📂 OpenFOAM Context**
> **ไฟล์:** **`system/fvSolution`**
>
> **บทบาท:** วางแผนวิธีแก้สมการเชิงเส้น $Ax=b$ และ Pressure-Velocity Coupling
>
> **คำสำคัญ (Keywords) ในไฟล์:**
> - **`solvers`** — ตั้งค่า Linear Solvers (PCG, PBiCGStab, smoothSolver)
>   - `solver` — เลือก algorithm (เช่น `PCG`, `PBiCGStab`)
>   - `preconditioner` — ช่วย加速 convergence (เช่น `DIC`, `DILU`)
>   - `tolerance` — ค่าความแม่นยำสัมบูรณ์ (เช่น `1e-06`)
>   - `relTol` — ค่าความแม่นยำสัมพัทธ์ (เช่น `0.01`)
> - **`SIMPLE`** — สำหรับ Steady-state (ภาพนิ่ง)
>   - `nNonOrthogonalCorrectors` — จำนวนรอบแก้ non-orthogonality
> - **`PISO`** — สำหรับ Transient (ภาพเคลื่อนไหว)
>   - `nCorrectors` — จำนวนรอบแก้ pressure ต่อ time step
>   - `nNonOrthogonalCorrectors` — จำนวนรอบแก้ non-orthogonality
> - **`PIMPLE`** — ผสม SIMPLE + PISO (สำหรับ transient ที่ใช้ large time step)
>   - `nOuterCorrectors` — จำนวนรอบ outer loop (แบบ SIMPLE)
>
> **ผลต่อการจำลอง:**
> - `tolerance` สูงไป → Convergence ไวแต่ไม่แม่น
> - `relTol` ต่ำไป → Convergence ช้า (เสียเวลา)
> - `nCorrectors` น้อยไป → Continuity error สูง
>
> **Best Practice:**
> - Pressure: `tolerance 1e-06`, `relTol 0.01`
> - Velocity: `tolerance 1e-05`, `relTol 0.1`
> - ถ้า mesh เบี้ยว → เพิ่ม `nNonOrthogonalCorrectors` (2-3)

เมื่อ `fvSchemes` แปลงโจทย์เป็นเมทริกซ์ $Ax = b$ แล้ว หน้าที่ของ `fvSolution` คือวางแผนเพื่อหาคำตอบ $x$ ออกมา

### Step-by-Step: เส้นทางการแก้สมการ

#### 1. การแก้เมทริกซ์ (Linear Solver)
**โจทย์:** มี $Ax=b$ จะหา $x$ อย่างไรให้เร็วที่สุด?
*   **Step 1: ดูลักษณะเมทริกซ์ ($A$)**
    *   **สมมาตร (Symmetric):** $A_{ij} = A_{ji}$ (เช่น สมการความดัน Laplacian)
        *   *Solver:* ใช้ **`PCG`** (Conjugate Gradient) + DIC Preconditioner — เร็วและแม่นสำหรับงานนี้
    *   **ไม่สมมาตร (Asymmetric):** $A_{ij} \neq A_{ji}$ (เช่น สมการความเร็วที่มี Convection)
        *   *Solver:* ใช้ **`PBiCGStab`** หรือ **`smoothSolver`** + DILU Preconditioner — รับมือความซับซ้อนได้ดี

#### 2. การเชื่อมโยงตัวแปร (Pressure-Velocity Coupling)
**โจทย์:** สมการความเร็ว ($U$) ต้องใช้ความดัน ($p$) แต่สมการความดันก็ต้องใช้ความเร็ว... มันเป็นงูกินหาง!
*   **Step 1: เลือกกลยุทธ์ตามประเภทงาน**
    *   **ภาพนิ่ง (Steady-state):** ใช้ **SIMPLE**
        *   *หลักการ:* "หม้อตุ๋น" — ไม่ต้องแม่นในแต่ละก้าว เดินหน้าไปเรื่อยๆ จนกว่าจะนิ่ง (Convergence)
    *   **ภาพเคลื่อนไหว (Transient):** ใช้ **PISO**
        *   *หลักการ:* "กระทะไฟแรง" — ทุกเสี้ยววินาทีต้องแม่นยำที่สุด วนแก้สมการความดันซ้ำๆ (`nCorrectors`) จนเป๊ะ
    *   **ลูกผสม (Transient + Large Time Step):** ใช้ **PIMPLE**
        *   *หลักการ:* รวมร่าง — ใช้วงนอก (Outer Loop) แบบ SIMPLE เพื่อความเสถียร และวงใน (Inner Loop) แบบ PISO เพื่อความแม่น ช่วยให้ใช้ Time Step ใหญ่ได้

#### 3. เกณฑ์การหยุด (Convergence Criteria)
**โจทย์:** คอมพิวเตอร์ไม่รู้ว่า "เสร็จแล้ว" คือเมื่อไหร่ เราต้องบอกมัน
*   **Step 1: ตั้งค่า Tolerance (ความแม่นยำสัมบูรณ์)**
    *   ถ้า Residual < `tolerance` (เช่น $10^{-6}$) → หยุดทันที ถือว่าแม่นพอแล้ว
*   **Step 2: ตั้งค่า RelTol (ความแม่นยำสัมพัทธ์)**
    *   ถ้า Residual ลดลงไปเยอะแล้วเมื่อเทียบกับตอนเริ่ม (เช่น 1% หรือ `0.01`) → หยุดได้ ไม่ต้องเค้นต่อ (เหมาะกับ Transient ที่เดี๋ยวก็แก้ใหม่)

---

### 3.1 โครงสร้างเมทริกซ์ $Ax = b$ ใน FVM (เบื้องหลัง)

> [!NOTE] **📂 OpenFOAM Context**
> **ไฟล์:** **`system/fvSolution`**
> **Section:** `solvers`
>
> **คำสำคัญ (Keywords):**
> - **Diagonal Dominance** — ค่า diagonal ต้องใหญ่กว่า off-diagonal (เพื่อความเสถียร)
> - **Symmetric Matrix** — ใช้ `PCG` (Conjugate Gradient)
> - **Asymmetric Matrix** — ใช้ `PBiCGStab` หรือ `smoothSolver`
> - **Preconditioner** — ช่วย加速 convergence (เช่น `DIC`, `DILU`, `GAMG`)
>
> **ตัวอย่างการตั้งค่า Solver:**
> ```cpp
> solvers
> {
>     // สมการสมมาตร (Symmetric) — เช่น Pressure
>     p
>     {
>         solver          PCG;               // Conjugate Gradient
>         preconditioner  DIC;               // Diagonal Incomplete Cholesky
>         tolerance       1e-06;
>         relTol          0.01;
>     }
>
>     // สมการไม่สมมาตร (Asymmetric) — เช่น Velocity
>     U
>     {
>         solver          PBiCGStab;         // Stabilized Bi-Conjugate Gradient
>         preconditioner  DILU;              // Diagonal Incomplete LU
>         tolerance       1e-05;
>         relTol          0.1;
>     }
> }
> ```
>
> **ผลกระทบ:**
> - Matrix ไม่ Diagonal Dominant → **ระเบิด (Divergence)**
> - Preconditioner ผิด → Convergence ช้า
> - Tolerance สูงไป → ผลลัพธ์ไม่แม่นยำ
>
> **Best Practice:** ตรวจสอบ Initial Residual ใน log file (ควรลดลงเรื่อยๆ)

เมื่อใช้ `fvm::` สร้างสมการ ผลลัพธ์คือ **Sparse Matrix**:

$$\begin{bmatrix}
a_{1,1} & a_{1,2} & 0 & \cdots & a_{1,n} \\
a_{2,1} & a_{2,2} & a_{2,3} & \cdots & 0 \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
a_{n,1} & 0 & 0 & \cdots & a_{n,n}
\end{bmatrix}
\begin{bmatrix}
x_1 \\ x_2 \\ \vdots \\ x_n
\end{bmatrix}
=
\begin{bmatrix}
b_1 \\ b_2 \\ \vdots \\ b_n
\end{bmatrix}$$

1.  **Diagonal ($a_{P,P}$):** ตัวเลขที่ "หนัก" ที่สุด (Dominant) ยิ่ง $\Delta t$ เล็ก ค่านี้ยิ่งเยอะ ยิ่งแก้ปัญหาง่าย
2.  **Off-diagonal ($a_{P,N}$):** ความสัมพันธ์กับเพื่อนบ้าน ถ้าสัมพันธ์กันเยอะ เมทริกซ์จะแน่นขึ้น
3.  **Source ($b$):** ขยะ (Terms) ที่เหลือทั้งหมดที่คำนวณค่าได้แล้ว จะถูกกวาดมาทิ้งไว้ฝั่งขวานี้

---

---

## 4. ตัวอย่างการแปลงร่าง: Time Derivative

> [!NOTE] **📂 OpenFOAM Context**
> **ไฟล์:** **`system/fvSchemes`**
> **Section:** `ddtSchemes`
>
> **ตัวอย่างการตั้งค่า:**
> ```cpp
> ddtSchemes
> {
>     default         Euler;             // 1st order (เสถียร)
>     // backward;                        // 2nd order (แม่นยำกว่า)
>     // CrankNicolson <φ>;               // 2nd order (สมดุล <φ> = 0.5-1.0)
> }
> ```
>
> **คำสำคัญ (Keywords):**
> - **`Euler`** — 1st order Implicit (เสถียรที่สุด แต่เบลอ)
> - **`backward`** — 2nd order Implicit (แม่นยำ ใช้ในงาน transient)
> - **`CrankNicolson`** — 2nd order (ผสมระหว่าง implicit/explicit)
>
> **ผลกระทบ:**
> - `Euler` → Δt ใหญ่ได้ แต่ผลลัพธ์เบลอ (Numerical Diffusion สูง)
> - `backward` → ต้องใช้ Δt เล็กกว่า แต่ผลลัพธ์แม่นยำ
> - Δt เล็กเกินไป → เสียเวลาคำนวณ
> - Δt ใหญ่เกินไป → **ระเบิด (Blow up)**
>
> **Best Practice:** เริ่มต้นด้วย `Euler` จนเสถียร แล้วค่อยเปลี่ยนเป็น `backward`
>
> **ควบคุม Δt:** ใช้ `maxCo` (Courant Number) ใน `system/controlDict`
> - Incompressible: `maxCo < 1.0`
> - Compressible: `maxCo < 0.5`

จาก **Calculus** (สมการอนุพันธ์) ไปเป็น **Algebra** (สมการเชิงเส้น) สำหรับเทอมของเวลา (Time Derivative) ตามหลักการ **Finite Volume Method (FVM)**:

### Step-by-Step: จาก Calculus สู่ Matrix ($Ax = b$)

สมมติเราพิจารณาเทอม **$\frac{\partial (\rho \phi)}{\partial t}$** ในสมการขนส่ง (Transport Equation)

#### 1. ขั้นตอน Calculus (The Starting Point)
เรามีอัตราการเปลี่ยนแปลงของ $\phi$ เทียบกับเวลาในเชิงทฤษฎี:
$$\frac{\partial (\rho \phi)}{\partial t}$$

#### 2. ขั้นตอน Integration (Volume Averaging)
ใน FVM เราไม่ได้คิดที่จุดใดจุดหนึ่ง แต่เรา "อินทิเกรต" ครอบคลุมปริมาตรของเซลล์ $V_P$ เพื่อดูการเปลี่ยนแปลงมวล/พลังงานรวมในก้อนนั้น:
$$\int_{V_P} \frac{\partial (\rho \phi)}{\partial t} dV$$
*ถ้าเราสมมติว่าค่าในเซลล์นั้นสม่ำเสมอ (Uniform) ผลการอินทิเกรตจะได้:*
$$\frac{\partial (\rho \phi)_P}{\partial t} V_P$$

#### 3. ขั้นตอน Discretization (เปลี่ยน Calculus เป็น Arithmetic)
เราต้องเปลี่ยน "อนุพันธ์" ($\partial t$) ให้กลายเป็น "ส่วนต่าง" ของเวลาที่จับต้องได้ ($\Delta t$) โดยใช้ **Euler Implicit Scheme**:
*   **$\phi^n$** = ค่า "ใหม่" (สิ่งที่เราต้องการหาใน Time Step นี้)
*   **$\phi^{n-1}$** = ค่า "เก่า" (รู้อยู่แล้วจาก Time Step ก่อนหน้า)

สมการจะกลายเป็น:
$$\frac{(\rho \phi)_P^n - (\rho \phi)_P^{n-1}}{\Delta t} V_P$$

#### 4. ขั้นตอน Algebra (จัดรูปเข้า Matrix $Ax = b$)
เพื่อจะแก้สมการ เราต้องแยกสิ่งที่ **ไม่รู้** (ฝั่งซ้าย - Matrix $A$) ออกจากสิ่งที่ **รู้แล้ว** (ฝั่งขวา - Vector $b$):

กระจายเทอมออกมา:
$$\left( \frac{\rho V_P}{\Delta t} \right) \phi_P^n - \left( \frac{\rho V_P}{\Delta t} \right) \phi_P^{n-1}$$

*   **ฝั่งซ้าย (Matrix $A$):** ค่า $\left( \frac{\rho V_P}{\Delta t} \right)$ จะถูกนำไปบวกเพิ่มใน **Diagonal** ของ Matrix $A$ ตรงตำแหน่งของเซลล์ $P$
*   **ฝั่งขวา (Vector $b$):** เทอม $\left( \frac{\rho V_P}{\Delta t} \right) \phi_P^{n-1}$ เป็นค่าที่รู้แล้ว จะถูกย้ายไปเป็น **Source Term** ในฝั่ง $b$

---

### สรุปประเด็นสำคัญ:
*   **ทำไม $\Delta t$ เล็กแล้วเสถียร?**
    ดูที่ตัวคูณของ $\phi_P^n$ ใน Matrix $A$ คือ $\frac{\rho V_P}{\Delta t}$ ถ้า $\Delta t$ ยิ่งน้อย ค่าตัวนี้จะยิ่ง **"ใหญ่มาก"** เมื่อเทียบกับค่าอื่นๆ ในแถวนั้น (Diagonal Dominance) ทำให้คอมพิวเตอร์แก้สมการได้ง่าย แม่นยำ และไม่ระเบิด
*   **การแปลงร่าง:**
    $\frac{\partial}{\partial t}$ $\rightarrow$ Calculus
    $\frac{\Delta}{\Delta t}$ $\rightarrow$ Discretization
    $A\phi = b$ $\rightarrow$ Algebra (Matrix)

---

## 5. การเขียนโค้ด: `createFields.H`

> [!NOTE] **📂 OpenFOAM Context**
> **ไฟล์:** **`createFields.H`** (อยู่ใน `src/` หรือสร้างเองใน solver)
>
> **บทบาท:** สร้างและเริ่มต้นตัวแปรฟิสิกส์ (Fields) ที่ใช้ในการจำลอง
>
> **คำสำคัญ (Keywords):**
> - **`IOobject`** — ระบุตำแหน่งไฟล์และวิธีการอ่าน/เขียน
> - **`volScalarField`**, **`volVectorField`** — Field ที่เก็บที่จุดกึ่งกลางเซลล์
> - **`surfaceScalarField`** — Field ที่เก็บที่ผิวหน้า (เช่น `phi`)
> - **`MUST_READ`**, **`AUTO_WRITE`** — ตั้งค่าการอ่าน/เขียนไฟล์
> - **`mesh`** — อ้างอิงถึง mesh object ปัจจุบัน
>
> **ตัวอย่างการใช้งาน:**
> ```cpp
> // สร้าง Pressure field
> volScalarField p
> (
>     IOobject
>     (
>         "p",                     // ชื่อไฟล์
>         runTime.timeName(),      // โฟลเดอร์เวลา (เช่น "0/")
>         mesh,
>         IOobject::MUST_READ,     // ต้องอ่านไฟล์
>         IOobject::AUTO_WRITE     // เขียนอัตโนมัติ
>     ),
>     mesh
> );
>
> // สร้าง Velocity field
> volVectorField U
> (
>     IOobject("U", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE),
>     mesh
> );
>
> // สร้าง Flux field (surface scalar)
> surfaceScalarField phi
> (
>     IOobject("phi", runTime.timeName(), mesh, IOobject::READ_IF_PRESENT, IOobject::AUTO_WRITE),
>     fvc::flux(U)              // คำนวณจาก velocity
> );
> ```
>
> **ผลกระทบ:**
> - ผิดพลาด → **Runtime Error** (ไม่พบไฟล์ `0/p`, `0/U`)
> - ลืม `MUST_READ` → Field เป็นค่าเริ่มต้น (ศูนย์) ทำให้ผลลัพธ์ผิด
>
> **Best Practice:** ตรวจสอบว่าไฟล์ `0/p`, `0/U` มีอยู่จริงก่อนรัน

นี่คือจุดเริ่มต้นของการสร้างตัวแปรใน OpenFOAM เราจะมาถอดรหัส Constructor นี้ทีละขั้น

### Step-by-Step: วิธีสร้างตัวแปร (Anatomy of a Field)

#### 1. เลือกประเภทตัวแปร (Class Selection)
**คำถาม:** ข้อมูลที่จะเก็บมีหน้าตาแบบไหน? และเก็บไว้ตรงไหนของ Mesh?
*   **Step 1: เลือก Geometric Type (เก็บที่ไหน)**
    *   `vol...` = เก็บที่ **จุดกึ่งกลางเซลล์** (ใช้บ่อยสุด เช่น $p, U, T$)
    *   `surface...` = เก็บที่ **ผิวหน้า** (ใช้กับ Flux เช่น `phi`)
*   **Step 2: เลือก Data Type (เก็บอะไร)**
    *   `...ScalarField` = เก็บ **ตัวเลขเดียว** (Scalar) เช่น ความดัน, อุณหภูมิ
    *   `...VectorField` = เก็บ **เวกเตอร์** (Vector) เช่น ความเร็ว

#### 2. สร้างบัตรประจำตัว (IOobject)
**คำถาม:** ตัวแปรนี้ชื่ออะไร? อ่านไฟล์ไหน? เขียนไฟล์ไหม?
```cpp
IOobject
(
    "p",                  // 1. ชื่อไฟล์บน Disk (สำคัญมาก!)
    runTime.timeName(),   // 2. โฟลเดอร์เวลาที่จะไปค้นหา (เช่น "0", "0.5")
    mesh,                 // 3. สังกัด Mesh ไหน (ปกติใช้ "mesh")
    IOobject::MUST_READ,  // 4. เงื่อนไขการอ่าน (Read Option)
    IOobject::AUTO_WRITE  // 5. เงื่อนไขการเขียน (Write Option)
)
```
*   **Decision Checklist:**
    *   *ต้องมีไฟล์ให้เริ่มรันไหม?*
        *   ใช่ (ตัวแปรหลัก $p, U$) → `MUST_READ` (หาไม่เจอให้ error)
        *   ไม่แน่ (ตัวแปรเสริม) → `READ_IF_PRESENT` (หาไม่เจอใช้ค่า default)
        *   ไม่ (ตัวแปรชั่วคราว) → `NO_READ`
    *   *อยากเก็บผลลัพธ์ลง Harddisk ไหม?*
        *   ใช่ → `AUTO_WRITE`
        *   ไม่ → `NO_WRITE`

#### 3. กำหนดสังกัดและค่าเริ่มต้น (Mesh & Value)
หลังจากยื่นบัตรประจำตัวแล้ว ต้องบอกว่าตัวแปรนี้เกาะอยู่กับ Mesh ไหน
```cpp
    mesh                // เกาะกับ Mesh นี้
    // (Optional) อาจใส่ค่าเริ่มต้นตรงนี้ได้ถ้าเลือก NO_READ
);
```

---

## 6. การวิเคราะห์ผล: `functionObjects`

> [!NOTE] **📂 OpenFOAM Context**
> **ไฟล์:** **`system/controlDict`**
> **Section:** `functions { ... }`
>
> **บทบาท:** คำนวณค่าทางวิศวกรรม (Forces, Coefficients, Probes, Sampling) ระหว่างรัน
>
> **คำสำคัญ (Keywords):**
> - **`functions`** — Block หลักที่เก็บ functionObjects ทั้งหมด
> - **`forceCoeffs`** — คำนวณ Lift/Drag Coefficients ($C_L, C_D$)
> - **`forces`** — คำนวณแรง (Force) โดยตรง
> - **`probes`** — วัดค่าที่จุดพิกัดเฉพาะ
> - **`sets`** — สร้างเส้น/ระนาบ sampling (เช่น แนวรากฐาน)
> - **`fieldMinMax`** — หาค่าสูงสุด/ต่ำสุดของ field
> - **`volFieldValue`** — คำนวณค่าเฉลี่ย/ผลรวมใน volume หนึ่งๆ
>
> **ตัวอย่างการตั้งค่า (Force Coefficients):**
> ```cpp
> functions
> {
>     forceCoeffs
>     {
>         type        forceCoeffs;
>         libs        ("libforces.so");
>
>         // ตั้งค่า Reference Values (สำคัญมาก!)
>         rho         rhoInf;           // ความหนาแน่น
>         magUInf     10.0;             // ความเร็วลมอิสระ [m/s]
>         lRef        1.0;              // ความยาวอ้างอิง [m]
>         Aref        1.0;              // พื้นที่อ้างอิง [m^2]
>
>         // ตั้งค่า Patch ที่จะคำนวณ
>         patches     ("airfoil");
>
>         // ตั้งค่า Direction
>         dragDir     (1 0 0);          // ทิศทางลม
>         liftDir     (0 1 0);          // ทิศทาง lift
>         pitchAxis   (0 0 1);          // แกนหมุน
>
>         // ตั้งค่า Output
>         writeFields yes;
>     }
> }
> ```
>
> **ผลกระทบ:**
> - `magUInf` ผิด → $C_L, C_D$ ผิด!
> - `Aref` ผิด → Scale ผิด!
> - ลืม `patches` → ไม่มี output
>
> **Best Practice:** ตรวจสอบ Reference Values ให้ถูกต้อง (หน่วย SI)

เราไม่ต้องเขียน Code ใหม่เพื่อคำนวณค่าทางวิศวกรรม OpenFOAM เตรียม "ปลั๊กอิน" ไว้ให้แล้ว

### Step-by-Step: การใช้งาน

1.  **Step 1: กำหนดเป้าหมาย**
    *   อยากรู้ Force Coefficients ($C_L, C_D$)?
    *   อยากรู้ค่าเฉลี่ย (Average)?
    *   อยากวัดค่าที่จุดใดจุดหนึ่ง (Probes)?

2.  **Step 2: ไปที่ `system/controlDict`**
    เพิ่ม Block `functions { ... }` ท้ายไฟล์

3.  **Step 3: ตั้งค่า (Configuration)**
    *   สำหรับ $C_L, C_D$ ต้องระวังเรื่อง **Reference Values** (ค่าอ้างอิง) ให้ดี:
        $$ C_F = \frac{F}{\frac{1}{2} \rho U_\infty^2 A_{ref}} $$
        *   `magUInf` (ความเร็วลมอิสระ) — *ใส่ผิด $C_L$ เพี้ยน*
        *   `Aref` (พื้นที่หน้าตัด) — *ใส่ผิด Scale เพี้ยน*
        *   `lRef` (ความยาว) — *ใช้คำนวณ Moment*

---

## 7. 📖 สรุปฉบับย่อ + Decision Trees

> [!NOTE] **📂 OpenFOAM Context** - **🗺️ Roadmap การตั้งค่า Case ทั้งหมด**
>
> **1. เริ่มต้น (Pre-processing):**
> - **`constant/polyMesh/`** — Mesh (จาก blockMesh/snappyHexMesh)
> - **`0/`** — Boundary Conditions เริ่มต้น
>
> **2. ตั้งค่า Physics:**
> - **`constant/transportProperties`** — คุณสมบัติของไหล (`nu`, `rho`, `mu`)
> - **`constant/turbulenceProperties`** — Turbulence Model (`kEpsilon`, `kOmegaSST`)
>
> **3. ตั้งค่า Numerics (สำคัญ!):**
> - **`system/fvSchemes`** — Discretization schemes
>   - `ddtSchemes`: `Euler` (เริ่มต้น) → `backward` (แม่นยำ)
>   - `gradSchemes`: `Gauss linear` (มาตรฐาน)
>   - `divSchemes`: `Gauss upwind` (เสถียร) → `limitedLinear` (สมดุล)
>   - `laplacianSchemes`: `Gauss linear corrected` (มาตรฐาน)
>
> **4. ตั้งค่า Solver (สำคัญ!):**
> - **`system/fvSolution`** — Linear Solvers และ Algorithm
>   - `solvers`: `PCG` (pressure), `PBiCGStab` (velocity)
>   - `SIMPLE` (steady) / `PISO` (transient) / `PIMPLE` (hybrid)
>   - `tolerance`: `1e-06` (pressure), `1e-05` (velocity)
>
> **5. ตั้งค่า Control:**
> - **`system/controlDict`** — Time stepping และ Output
>   - `deltaT` / `adjustTimeStep yes` + `maxCo`
>   - `writeInterval` — ความถี่ในการบันทึกผลลัพธ์
>   - `functions` — functionObjects (forces, probes)
>
> **6. รัน Simulation:**
> ```bash
> # ตรวจสอบ mesh
> checkMesh
>
> # รัน (redirect log)
> simpleFoam > log.simpleFoam 2>&1 &
>
> # monitor residuals
> tail -f log.simpleFoam
> ```
>
> **7. Post-processing:**
> - **ParaView** — ดูภาพผลลัพธ์
> - **`postProcessing/`** — ผลลัพธ์จาก functionObjects

### 7.1 สมการ → Code Mapping (สรุปภาพรวม)

| สมการฟิสิกส์ | Mathematical Term | OpenFOAM Code | fvm vs fvc |
|----------------|------------------|--------------|------------|
| **Time Derivative** | $\frac{\partial (\rho \phi)}{\partial t}$ | `fvm::ddt(rho, phi)` | fvm (implicit) |
| **Convection** | $\nabla \cdot (\rho \mathbf{u})$ | `fvm::div(phi, phi)` | fvm (implicit) |
| **Diffusion** | $\nabla \cdot (\Gamma \nabla \phi)$ | `fvm::laplacian(Gamma, phi)` | fvm (implicit) |
| **Pressure Gradient** | $-\nabla p$ | `fvc::grad(p)` | fvc (explicit) |
| **Divergence** | $\nabla \cdot (\rho \mathbf{u})$ | `fvc::div(phi)` | fvc (explicit) |

### 7.2 Decision Tree: เลือก Solver อย่างไร?

```
เริ่มต้น
    ↓
คำนวณ Reynolds Number: Re = ρUL/μ
    ↓
    ├─ Re < 2300 (Laminar)
    │     ↓
    │   ใช้ `icoFoam` (incompressible laminar)
    │
    └─ Re > 4000 (Turbulent)
          ↓
          คำนวณ Mach Number: Ma = U/c
          ↓
          ├─ Ma < 0.3 (Incompressible)
          │     ↓
          │   Steady? ──yes──> `simpleFoam` + turbulence model
          │      │
          │      └─no──> `pimpleFoam` + turbulence model
          │
          └─ Ma > 0.3 (Compressible)
                ↓
                Steady? ──yes──> `rhoSimpleFoam`
                     │
                     └─no──> `rhoPimpleFoam` หรือ `sonicFoam`
```

### 7.3 Decision Tree: เลือก Discretization Schemes

```
divSchemes (Convection):
    ↓
    Flow สงบ (ไม่มี shock)?
    ↓
    ├─ Yes → `Gauss linear` (แม่นยำสูง)
    │
    └─ No (Flow รุนแรง, ค่ากระโดก)
          ↓
          `Gauss upwind` (เสถียร) หรือ
          `Gauss linearUpwind` (สมดุลระหว่างแม่น/เสถียร)

laplacianSchemes (Diffusion):
    ↓
    Mesh สวย (orthogonal)?
    ↓
    ├─ Yes → `Gauss linear uncorrected` (เร็ว)
    │
    └─ No (Mesh เบี้ยว)
          ↓
          Non-orthogonality < 70°?
          ↓
          ├─ Yes → `Gauss linear corrected` (แนะนำ)
          │
          └─ No (> 70°) → `Gauss linear limited` (ป้องกันระเบิด)
```

### 7.4 Decision Tree: Pressure-Velocity Coupling

```
เลือก Algorithm:
    ↓
    Steady-state (ภาพนิ่ง)?
    ↓
    ├─ Yes → `SIMPLE`
    │         - ใช้ under-relaxation factors
    │         - Iterate จนถึง convergence
    │
    └─ No (Transient - ภาพเคลื่อนไหว)
          ↓
          Time step เล็กมาก?
          ↓
          ├─ Yes → `PISO`
          │        - แก้ pressure หลายรอบต่อ time step
          │        - nCorrectors: 2-3
          │
          └─ No (Time step ใหญ่)
                ↓
                `PIMPLE`
                - ผสม SIMPLE + PISO
                - nOuterCorrectors > 1: ให้ large time steps
```

### 7.5 Common Pitfalls และวิธีแก้

| ปัญหา                                 | สาเหตุ                                                            | วิธีแก้                                                                                       |
| ------------------------------------- | ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Simulation ระเบิด (Blow up)**       | - Time step ใหญ่เกินไป<br>- Schemes ไม่เสถียร<br>- BCs ขัดแย้งกัน | - ลด `deltaT`<br>- เปลี่ยนเป็น `Gauss upwind`<br>- ตรวจสอบ `0/` BCs                           |
| **Residuals ไม่ลู่เข้า**              | - Mesh คุณภาพต่ำ<br>- Tolerance สูงไป<br>- Under-relaxation สูงไป | - ปรับปรุง mesh (checkMesh)<br>- ลด `tolerance`, `relTol`<br>- ลด relaxation factors          |
| **Continuity errors สูง**             | - `phi` ไม่ถูกต้อง<br>- Pressure-velocity coupling ไม่ดี          | - เพิ่ม `nCorrectors`<br>- เพิ่ม `nNonOrthogonalCorrectors`<br>- ใช้ `Gauss linear corrected` |
| **ผลลัพธ์เบลอ (Numerical diffusion)** | - `Gauss upwind`<br>- Mesh หยาบเกินไป                             | - เปลี่ยนเป็น `Gauss linear`<br>- Refine mesh<br>- ใช้ `linearUpwind` or `limitedLinear`      |

### 7.6 Quick Reference: Config Files

**`system/fvSchemes` — ควบคุมความแม่น:**
```cpp
ddtSchemes { default Euler; }           // Time stepping
gradSchemes { default Gauss linear; }   // Gradient calculation
divSchemes { default Gauss upwind; }    // Convection (key for stability!)
laplacianSchemes { default Gauss linear corrected; }  // Diffusion
```

**`system/fvSolution` — ควบคุมความเสถียร:**
```cpp
solvers
{
    p { solver PCG; preconditioner DIC; tolerance 1e-06; relTol 0.01; }
    U { solver PBiCGStab; preconditioner DILU; tolerance 1e-05; relTol 0.1; }
}
SIMPLE { nNonOrthogonalCorrectors 0; }
PISO { nCorrectors 2; }
```

**`constant/transportProperties` — คุณสมบัติของไหล:**
```cpp
nu          [0 2 -1 0 0 0 0]  1e-05;  // Kinematic viscosity [m²/s]
// หรือ
mu          [1 -1 -1 0 0 0 0]  1.8e-05;  // Dynamic viscosity [kg/(m·s)]
rho         [1 -3 0 0 0 0 0]   1000;     // Density [kg/m³]
```

**`constant/turbulenceProperties` — Turbulence model:**
```cpp
simulationType  RAS;                    // หรือ LES, laminar
RAS
{
    RASModel        kEpsilon;           // k-ε model (industry standard)
    // RASModel        kOmegaSST;        // k-ω SST (better for adverse pressure gradients)
    turbulence      on;
}
```

---

## 8. 🎯 สรุปท้ายบท: 3 หลักในการเข้าใจ OpenFOAM

### หลักที่ 1: เข้าใจฟิสิกส์ (กำแพงกว่าจะไป code)
1. **3 สมการควบคุม:** Continuity → Momentum → Energy
2. **เลขไร้มิติ:** Reynolds ($Re$) → Laminar vs Turbulent, Mach ($Ma$) → Compressibility
3. **Flow regime ขึ้นกับ:** Solver selection, Turbulence modeling, Boundary conditions

### หลักที่ 2: เข้าใจ discretization (กำแพงเรื่องความแม่น/เสถียร)
1. **`fvm` vs `fvc`:** fvm = Implicit (เสถียร), fvc = Explicit (เร็ว)
2. **Schemes:** `Gauss upwind` (เสถียร) vs `Gauss linear` (แม่นยำ)
3. **Non-orthogonality:** ใช้ `corrected` สำหรับ mesh จริง

### หลักที่ 3: เข้าใจ code structure (กำแพง debug)
1. **Field classes:** `vol...Field` (cell centers) vs `surface...Field` (faces)
2. **Matrix assembly:** $Ax=b$ จาก `fvm::` จะถูกแก้ด้วย solvers ใน `fvSolution`
3. **Tolerance:** `tolerance` (absolute) vs `relTol` (relative) ควบคุมการหยุด iterate

---

## 9. 📚 แหล่งอ้างอิงที่เป็นประโยชน์

- **OpenFOAM User Guide:** https://www.openfoam.com/documentation/user-guide/
- **OpenFOAM Programmer's Guide:** https://www.openfoam.com/documentation/programmers-guide/
- **Cavity Tutorial:** `tutorials/incompressible/icoFoam/cavity/` (เริ่มต้นที่ดีที่สุด!)
- **Mesh Quality:** `checkMesh` command → อ่าน output เพื่อดู non-orthogonality
- **Log Files:** `log.simpleFoam`, `log.pimpleFoam` → monitor residuals และ continuity errors

---

**สรุปสั้นๆ จำง่ายๆ:**
*   **`divSchemes`** = เลือกวิธีลากเส้น (ส่งผลต่อความแม่น/ความเบลอ)
*   **`laplacianSchemes`** = เลือกวิธีหาความชัน (ส่งผลต่อการจัดการ Mesh เบี้ยว)
*   **`fvSolution`** = เลือกวิธีคิดเลข (ส่งผลต่อความเร็ว/ความนิ่ง)
*   **Code** = การสร้างตัวแปรต้องมี "บัตรประจำตัว" (`IOobject`)