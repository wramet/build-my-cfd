# 🧭 OpenFOAM Content-Code Navigation Hub (Module 01)

> [!TIP] **ทำไม Module 01 ถึงสำคัญ?**
> โมดูลนี้เป็นรากฐานที่จำเป็นก่อนการจำลองทุกครั้ง หากคุณไม่เข้าใจสมการที่ควบคุม (Governing Equations) การ discretization ที่ถูกต้อง และการกำหนด Boundary Conditions ที่เหมาะสม การจำลองของคุณอาจแตก (diverge) หรือให้ผลลัพธ์ที่ผิดพลาด ทำให้เสียเวลาและทรัพยากรในการคำนวณ การเข้าใจหลักการเหล่านี้จะช่วยให้คุณแก้ปัญหาเมื่อเกิด error และปรับแต่งการตั้งค่า (settings) ได้อย่างมั่นใจ
> **สำหรับการจำลอง:** ทุกสิ่งในโมดูลนี้จะถูกนำไปใช้ในไฟล์ case directory ของคุณ โดยเฉพาะ `0/`, `constant/`, และ `system/`

ยินดีต้อนรับสู่ศูนย์กลางการนำทางสำหรับ **Module 01: CFD Fundamentals** หน้านี้ถูกออกแบบมาเพื่อช่วยให้คุณเชื่อมโยง **"ทฤษฎี" (Documentation)** เข้ากับ **"การลงมือทำจริง" (Source Code)** ใน OpenFOAM

OpenFOAM เป็นซอฟต์แวร์ที่ขับเคลื่อนด้วยโค้ด C++ ที่ซับซ้อน การเข้าใจว่าทฤษฎี CFD ถูกแปลงเป็นโค้ดอย่างไรเป็นกุญแจสำคัญสู่ความเชี่ยวชาญ

---

## 📚 1. Governing Equations (สมการควบคุม)

> [!NOTE] **📂 OpenFOAM Context**
> สมการเหล่านี้ถูกนำไปใช้ใน **Domain A: Physics & Fields** โดย:
> - ไฟล์ `0/` สำหรับกำหนดค่าเริ่มต้นและเงื่อนไขขอบเขตของ pressure (`p`), velocity (`U`), turbulence fields (`k`, `epsilon`, `omega`)
> - ไฟล์ `constant/transportProperties` สำหรับกำหนดค่าความหนืด (viscosity `nu`) และความหนาแน่น (density `rho`)
> - ไฟล์ `constant/turbulenceProperties` สำหรับเลือก turbulence model
>
> **Keywords สำคัญ:** `nu`, `rho`, `p`, `U`, `k`, `epsilon`, `omega`, `RASModel`, `LESModel`

เรียนรู้สมการพื้นฐานที่ปกครองพฤติกรรมของของไหลและดูว่าพวกมันถูกประกาศใน OpenFOAM อย่างไร

| หัวข้อ (Topic) | เอกสารประกอบ (Documentation) | ตำแหน่งโค้ด OpenFOAM (Code Location) |
|---|---|---|
| **Navier-Stokes Equations** | [01_Navier_Stokes.md](CONTENT/01_GOVERNING_EQUATIONS/01_Navier_Stokes.md) | `src/finiteVolume/cfdTools/general/include/fvCFD.H` |
| **Continuity Equation** | [02_Continuity_Equation.md](CONTENT/01_GOVERNING_EQUATIONS/02_Continuity_Equation.md) | `src/finiteVolume/cfdTools/general/include/fvCFD.H` |
| **Turbulence Modeling** | [06_Turbulence_Modeling.md](CONTENT/01_GOVERNING_EQUATIONS/06_Turbulence_Modeling.md) | `src/TurbulenceModels` |
| **Conservation Laws** | [03_Conservation_Laws.md](CONTENT/01_GOVERNING_EQUATIONS/03_Conservation_Laws.md) | `src/finiteVolume/fvMatrices` |

---

## 📐 2. Finite Volume Method (ระเบียบวิธีปริมาตรจำกัด)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain B: Numerics & Linear Algebra** โดยตรง:
> - ไฟล์ `system/fvSchemes` สำหรับเลือก discretization schemes เช่น `gradSchemes`, `divSchemes`, `laplacianSchemes`
> - ไฟล์ `system/fvSolution` สำหรับตั้งค่า linear solvers, algorithms (SIMPLE, PISO, PIMPLE), และ tolerances
> - ไฟล์ `system/controlDict` สำหรับควบคุมเวลา (time step `deltaT`) และ write intervals
>
> **Keywords สำคัญ:** `Gauss linear`, `Gauss upwind`, `linearUpwind`, `UEqn`, `pEqn`, `solvers`, `tolerances`, `relTol`

สำรวจวิธีการแปลงสมการอนุพันธ์ (PDEs) ให้อยู่ในรูปสมการพีชคณิตที่คอมพิวเตอร์เข้าใจ (Discretization)

| หัวข้อ (Topic) | เอกสารประกอบ (Documentation) | ตำแหน่งโค้ด OpenFOAM (Code Location) |
|---|---|---|
| **Discretization Schemes (Overview)** | [02_Discretization_Schemes.md](CONTENT/02_FINITE_VOLUME_METHOD/02_Discretization_Schemes.md) | `src/finiteVolume/finiteVolume/fvSchemes` |
| **Divergence Schemes (Convection)** | [02_Discretization_Schemes.md](CONTENT/02_FINITE_VOLUME_METHOD/02_Discretization_Schemes.md) | `src/finiteVolume/finiteVolume/divSchemes` |
| **Gradient Schemes** | [02_Discretization_Schemes.md](CONTENT/02_FINITE_VOLUME_METHOD/02_Discretization_Schemes.md) | `src/finiteVolume/finiteVolume/gradSchemes` |
| **Laplacian Schemes (Diffusion)** | [02_Discretization_Schemes.md](CONTENT/02_FINITE_VOLUME_METHOD/02_Discretization_Schemes.md) | `src/finiteVolume/finiteVolume/laplacianSchemes` |
| **Matrix Assembly (fvMatrix)** | [03_Matrix_Assembly.md](CONTENT/02_FINITE_VOLUME_METHOD/03_Matrix_Assembly.md) | `src/finiteVolume/fvMatrices/fvMatrix/fvMatrix.C` |
| **Time Discretization (ddt)** | [04_Time_Discretization.md](CONTENT/02_FINITE_VOLUME_METHOD/04_Time_Discretization.md) | `src/finiteVolume/finiteVolume/ddtSchemes` |

---

## 🚧 3. Boundary Conditions (เงื่อนไขขอบเขต)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain A: Physics & Fields** โดยเฉพาะ:
> - ไฟล์ในโฟลเดอร์ `0/` (เช่น `0/U`, `0/p`, `0/k`, `0/epsilon`) สำหรับกำหนด boundary condition types
> - ไฟล์ `constant/polyMesh/boundary` สำหรับนิยาม boundary patches และ types (เช่น `patch`, `wall`, `symmetryPlane`)
>
> **Keywords สำคัญ:** `fixedValue`, `zeroGradient`, `fixedFluxPressure`, `inletOutlet`, `noSlip`, `freestream`, `wallFunctions`

ทำความเข้าใจวิธีกำหนดเงื่อนไขที่ขอบของโดเมน ซึ่งเป็นสิ่งที่ทำให้แต่ละปัญหา CFD แตกต่างกัน

| หัวข้อ (Topic) | เอกสารประกอบ (Documentation) | ตำแหน่งโค้ด OpenFOAM (Code Location) |
|---|---|---|
| **Boundary Conditions Overview** | [00_Overview.md](CONTENT/03_BOUNDARY_CONDITIONS/00_Overview.md) | `src/finiteVolume/fields/fvPatchFields` |
| **Fixed Value (Dirichlet)** | [05_Common_Boundary_Conditions.md](CONTENT/03_BOUNDARY_CONDITIONS/05_Common_Boundary_Conditions.md) | `src/finiteVolume/fields/fvPatchFields/basic/fixedValue` |
| **Zero Gradient (Neumann)** | [05_Common_Boundary_Conditions.md](CONTENT/03_BOUNDARY_CONDITIONS/05_Common_Boundary_Conditions.md) | `src/finiteVolume/fields/fvPatchFields/basic/zeroGradient` |
| **Inlet/Outlet Conditions** | [06_Advanced_Boundary_Conditions.md](CONTENT/03_BOUNDARY_CONDITIONS/06_Advanced_Boundary_Conditions.md) | `src/finiteVolume/fields/fvPatchFields/derived/inletOutlet` |
| **Wall Functions** | [06_Advanced_Boundary_Conditions.md](CONTENT/03_BOUNDARY_CONDITIONS/06_Advanced_Boundary_Conditions.md) | `src/TurbulenceModels/turbulenceModels/derivedFvPatchFields/wallFunctions` |

---

## 🚀 4. First Simulation (การจำลองครั้งแรก)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้รวมทุก Domain เข้าด้วยกันใน **Complete Case Setup**:
> - **Domain A:** โฟลเดอร์ `0/` สำหรับ field initializations และ boundary conditions
> - **Domain B:** ไฟล์ `system/fvSchemes` และ `system/fvSolution` สำหรับ numerical settings
> - **Domain C:** ไฟล์ `system/controlDict` สำหรับ simulation time control และ output
> - **Domain D:** ไฟล์ `system/blockMeshDict` สำหรับ mesh generation (ถ้าใช้ blockMesh)
>
> **Keywords สำคัญ:** `icoFoam`, `simpleFoam`, `startTime`, `endTime`, `deltaT`, `writeControl`, `application`, `startFrom`

นำทฤษฎีมาสู่การปฏิบัติจริงด้วยการจำลองปัญหาคลาสสิก: Lid-Driven Cavity Flow

| หัวข้อ (Topic) | เอกสารประกอบ (Documentation) | ตำแหน่งโค้ด/ตัวอย่าง OpenFOAM (Code Location) |
|---|---|---|
| **Lid-Driven Cavity Case** | [03_The_Lid-Driven_Cavity_Problem.md](CONTENT/04_FIRST_SIMULATION/03_The_Lid-Driven_Cavity_Problem.md) | `tutorials/incompressible/icoFoam/cavity/cavity` |
| **icoFoam Solver Code** | [02_The_Workflow.md](CONTENT/04_FIRST_SIMULATION/02_The_Workflow.md) | `applications/solvers/incompressible/icoFoam/icoFoam.C` |
| **Simulation Workflow** | [02_The_Workflow.md](CONTENT/04_FIRST_SIMULATION/02_The_Workflow.md) | `system/controlDict`, `system/fvSchemes`, `system/fvSolution` |

---

> [!TIP] **วิธีการใช้งาน**
> 1.  อ่าน **เอกสารประกอบ** เพื่อเข้าใจหลักการทฤษฎี
> 2.  เปิด **ตำแหน่งโค้ด OpenFOAM** ใน Text Editor หรือ IDE ของคุณเพื่อดูการเขียนโค้ดจริง (C++)
> 3.  พยายามเชื่อมโยงสมการคณิตศาสตร์ในเอกสาร เข้ากับบรรทัดของโค้ดในไฟล์ `.C` หรือ `.H`
