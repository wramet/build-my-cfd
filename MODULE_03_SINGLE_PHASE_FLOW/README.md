# Module 03: Single Phase Flow (การไหลแบบเฟสเดียว)

> [!TIP] สำคัญอย่างยิ่งสำหรับความสำเร็จในการจำลอง
> โมดูลนี้เป็น **หัวใจสำคัญ** ของการใช้ OpenFOAM สำหรับการงานวิศวกรรมจริง หากเข้าใจหลักการในโมดูลนี้ คุณจะสามารถ:
> - เลือก **Solver** ที่เหมาะสมกับปัญหาของคุณ (Domain C: `system/controlDict`, Domain E: `src/`)
> - ตั้งค่า **Pressure-Velocity Coupling** ที่ถูกต้องเพื่อให้ Simulation บรรลุความเสถียร (Domain B: `system/fvSolution`)
> - เลือกและตั้งค่า **Turbulence Model** ที่เหมาะสมกับ Flow ของคุณ (Domain A: `constant/turbulenceProperties`, `0/`)
> - จัดการ **Heat Transfer** และ **Buoyancy** ได้อย่างมั่นใจ (Domain A: `0/`, `constant/thermophysicalProperties`)
> - ทำ **Validation** เพื่อให้มั่นใจว่าผลลัพธ์ถูกต้อง (Domain C: `system/controlDict` - `functions`)
>
> **การเชื่อมโยงกับ OpenFOAM:** ทุกหัวข้อในโมดูลนี้จะเชื่อมโยงโดยตรงกับไฟล์ภายใน OpenFOAM Case directory (`0/`, `constant/`, `system/`)

## 📋 ภาพรวม (Overview)

โมดูลนี้ครอบคลุมหลักการและการประยุกต์ใช้ CFD สำหรับการไหลแบบเฟสเดียว (Single Phase Flow) ใน OpenFOAM อย่างครบถ้วน ตั้งแต่พื้นฐานของ Solver คณิตศาสตร์เบื้องหลังการแก้สมการ Navier-Stokes การจัดการกับความปั่นป่วน (Turbulence) ไปจนถึงการถ่ายเทความร้อน (Heat Transfer) และการตรวจสอบความถูกต้องของผลลัพธ์ (V&V)

## 📚 โครงสร้างเนื้อหา (Module Structure)

### 1. Incompressible Flow Solvers (Solver สำหรับการไหลแบบอัดตัวไม่ได้)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain C: Simulation Control** & **Domain E: Solver Selection**
>
> หัวข้อนี้เชื่อมโยงกับ:
> - **`system/controlDict`**: คุณสมบัติสำคัญคือ `application` (ระบุ Solver เช่น `icoFoam`, `simpleFoam`), `startFrom`, `startTime`, `stopAt`, `endTime`, `deltaT`, `writeControl`
> - **Solver Command**: วิธีการ run solver เช่น `simpleFoam`, `icoFoam`, `pimpleFoam`
> - **Directory Structure**: การจัดโครงสร้าง Case (`0/`, `constant/`, `system/`)
>
> **การนำไปใช้:** เมื่อเข้าใจ Solver แต่ละตัว คุณจะรู้ว่า:
> - `icoFoam` → Transient, incompressible, laminar flow
> - `simpleFoam` → Steady-state, incompressible, turbulent flow
> - `pimpleFoam` → Transient, incompressible, turbulent flow

📂 [ไปที่เนื้อหา](CONTENT/01_INCOMPRESSIBLE_FLOW_SOLVERS/00_Overview.md)
เรียนรู้เกี่ยวกับ Solver พื้นฐานและการควบคุมการจำลอง
*   [01_Introduction.md](CONTENT/01_INCOMPRESSIBLE_FLOW_SOLVERS/01_Introduction.md): บทนำสูการไหลแบบอัดตัวไม่ได้
*   [02_Standard_Solvers.md](CONTENT/01_INCOMPRESSIBLE_FLOW_SOLVERS/02_Standard_Solvers.md): เจาะลึก icoFoam และ simpleFoam
*   [03_Simulation_Control.md](CONTENT/01_INCOMPRESSIBLE_FLOW_SOLVERS/03_Simulation_Control.md): การควบคุมเวลาและการเขียนผลลัพธ์

### 2. Pressure-Velocity Coupling (การควบคู่ความดัน-ความเร็ว)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain B: Numerics & Linear Algebra** & **Domain A: Physics & Fields**
>
> หัวข้อนี้เชื่อมโยงกับ:
> - **`system/fvSolution`**: คำสั่งสำคัญคือ `solvers` (ตั้งค่า solver สำหรับ `p`, `U`) และ `algorithms` (SIMPLE/PISO/PIMPLE settings)
>   - **SIMPLE**: ใช้สำหรับ steady-state (`simpleFoam`) คีย์เวิร์ด: `SIMPLE { nNonOrthogonalCorrectors; ... }`
>   - **PISO**: ใช้สำหรับ transient (`icoFoam`, `pisoFoam`) คีย์เวิร์ด: `PISO { nCorrectors; nNonOrthogonalCorrectors; ... }`
>   - **PIMPLE**: ใช้สำหรับ transient ที่ต้องการ stability สูง (`pimpleFoam`) คีย์เวิร์ด: `PIMPLE { nCorrectors; nOuterCorrectors; ... }`
> - **`system/fvSchemes`**: คีย์เวิร์ด `divSchemes` และ `gradSchemes` สำหรับการ discretize สมการ
> - **Boundary Conditions**: ใน `0/p`, `0/U` มีผลต่อความเสถียรของการแก้สมการ
>
> **การนำไปใช้:** การเข้าใจ Algorithm เหล่านี้ช่วยให้คุณ:
> - ปรับ `nCorrectors`, `nOuterCorrectors` ให้ Simulation บรรลุความเสถียร
> - เลือกสัดส่วน `underRelaxationFactor` สำหรับ SIMPLE algorithm

📂 [ไปที่เนื้อหา](CONTENT/02_PRESSURE_VELOCITY_COUPLING/00_Overview.md)
เข้าใจอัลกอริทึมหัวใจสำคัญของ CFD
*   [01_Mathematical_Foundation.md](CONTENT/02_PRESSURE_VELOCITY_COUPLING/01_Mathematical_Foundation.md): พื้นฐานทางคณิตศาสตร์
*   [02_SIMPLE_Algorithm.md](CONTENT/02_PRESSURE_VELOCITY_COUPLING/02_SIMPLE_Algorithm.md): เจาะลึก SIMPLE Algorithm
*   [03_PISO_and_PIMPLE_Algorithms.md](CONTENT/02_PRESSURE_VELOCITY_COUPLING/03_PISO_and_PIMPLE_Algorithms.md): เจาะลึก PISO และ PIMPLE
*   [04_Rhie_Chow_Interpolation.md](CONTENT/02_PRESSURE_VELOCITY_COUPLING/04_Rhie_Chow_Interpolation.md): การแก้ปัญหา Checkerboarding
*   [05_Algorithm_Comparison.md](CONTENT/02_PRESSURE_VELOCITY_COUPLING/05_Algorithm_Comparison.md): การเปรียบเทียบและการเลือกใช้

### 3. Turbulence Modeling (แบบจำลองความปั่นป่วน)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain A: Physics & Fields** & **Domain B: Numerics**
>
> หัวข้อนี้เชื่อมโยงกับ:
> - **`constant/turbulenceProperties`**: คีย์เวิร์ด `simulationType` (RAS, LES, DES) และ `RASModel` (kEpsilon, kOmegaSST, etc.) หรือ `LESModel`
> - **`constant/transportProperties`**: คีย์เวิร์ด `nu` (kinematic viscosity) สำหรับ laminar flow
> - **`0/` directory**: Field files สำหรับ:
>   - `k` (turbulent kinetic energy)
>   - `epsilon` (dissipation rate) หรือ `omega` (specific dissipation rate)
>   - `nut` (turbulent viscosity)
>   - `nuTilda` (Spalart-Allmaras variable)
> - **`system/fvSchemes`**: คีย์เวิร์ด `divSchemes` สำหรับ discretize turbulence terms (เช่น `div(phi,k)`, `div(phi,epsilon)`)
> - **Wall Functions**: ใน `0/k`, `0/epsilon`, `0/omega` boundary conditions ที่ผนัง
>
> **การนำไปใช้:** การเลือก Turbulence Model และ Wall Treatment ที่ถูกต้อง:
> - High Re flow + coarse mesh → Wall functions (`kqRWallFunction`, `epsilonWallFunction`)
> - Low Re flow + fine mesh → Low Re models (`omegaWallFunction`) ต้อง Y+ < 1
> - `kEpsilon`: ดีสำหรับ free-shear flows, แต่ไม่แม่นยำที่ผนัง
> - `kOmegaSST`: ดีสำหรับ flows ที่มี adverse pressure gradient และ near-wall

📂 [ไปที่เนื้อหา](CONTENT/03_TURBULENCE_MODELING/00_Overview.md)
การจัดการกับการไหลแบบปั่นป่วนในระดับอุตสาหกรรม
*   [01_Turbulence_Fundamentals.md](CONTENT/03_TURBULENCE_MODELING/01_Turbulence_Fundamentals.md): ธรรมชาติของความปั่นป่วน
*   [02_RANS_Models.md](CONTENT/03_TURBULENCE_MODELING/02_RANS_Models.md): แบบจำลอง RANS (k-epsilon, k-omega)
*   [03_Wall_Treatment.md](CONTENT/03_TURBULENCE_MODELING/03_Wall_Treatment.md): การจัดการที่ผนังและ Y+
*   [04_LES_Fundamentals.md](CONTENT/03_TURBULENCE_MODELING/04_LES_Fundamentals.md): พื้นฐาน Large Eddy Simulation

### 4. Heat Transfer (การถ่ายเทความร้อน)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain A: Physics & Fields** & **Domain B: Numerics**
>
> หัวข้อนี้เชื่อมโยงกับ:
> - **Solver Selection**: ใช้ solvers ที่รองรับ Heat Transfer:
>   - `buoyantSimpleFoam` → Steady-state, buoyancy-driven flow
>   - `buoyantPimpleFoam` → Transient, buoyancy-driven flow
>   - `chtMultiRegionFoam` → Conjugate Heat Transfer (solid + fluid)
> - **`constant/thermophysicalProperties`**: คีย์เวิร์ด:
>   - `transport` (viscosity model: `const`, `sutherland`)
>   - `thermodynamics` (equation of state: `perfectGas`, `incompressiblePerfectGas`)
>   - `energy` (energy specification: `sensibleEnthalpy`, `sensibleInternalEnergy`)
> - **`0/` directory**: Field files สำหรับ:
>   - `T` (temperature)
>   - `p` (pressure - สำหรับ compressible solvers)
>   - `p_rgh` (reduced pressure - สำหรับ buoyant solvers)
> - **`constant/turbulenceProperties`**: Buoyancy effects (เช่น `buoyancyTurbulence` on/off)
> - **Boundary Conditions**: ใช้ `fixedValue`, `fixedGradient`, `externalWallHeatFlux`, `compressible::turbulentTemperatureCoupledBaffleMixed` (สำหรับ CHT)
>
> **การนำไปใช้:**
> - Natural Convection → ต้องมีการตั้งค่า `g` (gravity) ใน `constant/g`
> - CHT → ต้องมีหลาย regions ใน `constant/` และตั้งค่า interface BCs

📂 [ไปที่เนื้อหา](CONTENT/04_HEAT_TRANSFER/00_Overview.md)
การรวมสมการพลังงานเข้ากับการไหล
*   [01_Energy_Equation_Fundamentals.md](CONTENT/04_HEAT_TRANSFER/01_Energy_Equation_Fundamentals.md): พื้นฐานสมการพลังงาน
*   [02_Heat_Transfer_Mechanisms.md](CONTENT/04_HEAT_TRANSFER/02_Heat_Transfer_Mechanisms.md): การนำ การพา และการแผ่รังสี
*   [03_Buoyancy_Driven_Flows.md](CONTENT/04_HEAT_TRANSFER/03_Buoyancy_Driven_Flows.md): แรงลอยตัวและ Natural Convection
*   [04_Conjugate_Heat_Transfer.md](CONTENT/04_HEAT_TRANSFER/04_Conjugate_Heat_Transfer.md): การถ่ายเทความร้อนร่วม (CHT)

### 5. Practical Applications (การประยุกต์ใช้งานจริง)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain C: Simulation Control** & **Domain A: Physics & Fields**
>
> หัวข้อนี้เชื่อมโยงกับ:
> - **`system/controlDict`**: `functions` สำหรับ post-processing:
>   - `forces` → คำนวณ lift/drag forces
>   - `forceCoeffs` → คำนวณ lift/drag coefficients
>   - `fieldAverage` → คำนวณค่าเฉลี่ยของ fields
>   - `probes` → ตรวจสอบค่าที่จุดวัด
>   - `surfaceSampling` → ดึงข้อมูลบน surfaces
> - **Boundary Conditions**: การเลือก BCs ที่เหมาะสมกับแต่ละ application:
>   - External Aerodynamics → `atmBoundaryLayerInlet`, `freestream`
>   - Internal Flow → `fixedValue`, `flowRateInletVelocity`, `zeroGradient`
>   - Heat Exchangers → `externalWallHeatFlux`, `turbulentTemperatureCoupledBaffleMixed`
> - **Mesh Quality**: การปรับ mesh ให้เหมาะกับ application (y+ calculation)
>
> **การนำไปใช้:** การนำความรู้ไปประยุกต์กับงานจริง เช่น:
> - วิเคราะห์ Drag coefficient ของรถยนต์
> - วิเคราะห์ Pressure drop ในท่อ
> - วิเคราะห์ Heat transfer ใน Heat Exchanger

📂 [ไปที่เนื้อหา](CONTENT/05_PRACTICAL_APPLICATIONS/00_Overview.md)
*   01_External_Aerodynamics.md
*   02_Internal_Flow_and_Piping.md
*   03_Heat_Exchangers.md

### 6. Validation and Verification (การตรวจสอบความถูกต้อง)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain C: Simulation Control** & **Domain A: Physics & Fields**
>
> หัวข้อนี้เชื่อมโยงกับ:
> - **`system/controlDict`**: `functions` สำหรับ V&V:
>   - `residuals` → ตรวจสอบค่า convergence ของสมการ
>   - `misc` → คำนวณค่า error norms
> - **Mesh Independence Studies**:
>   - สร้าง meshes หลายขนาด (coarse → medium → fine)
>   - เปลี่ยน mesh โดยไม่ต้องเปลี่ยน settings อื่น (ใช้ `refinementLevels` ใน `snappyHexMeshDict` หรือ `blockMeshDict`)
>   - ตรวจสอบ `writePrecision` ใน `controlDict`
> - **Experimental Validation**:
>   - ใช้ `probes` ใน `controlDict` เพื่อบันทึกค่าที่ตำแหน่งเดียวกับ experiment
>   - ใช้ `sampleDict` (หรือ `surfaces` function) เพื่อเปรียบเทียบ profiles
> - **Numerical Verification**:
>   - `tolerances` ใน `system/fvSolution` → ปรับค่า `solver`, `tolerance`, `relTol`
>   - `schemes` ใน `system/fvSchemes` → เปลี่ยนจาก `upwind` เป็น `linearUpwind` หรือ `Gauss linear` เพื่อทดสอบ sensitivity
>
> **การนำไปใช้:** เพื่อให้มั่นใจว่าผลลัพธ์ถูกต้อง:
> - Mesh independence → ผลลัพธ์ไม่เปลี่ยนแปลงเมื่อละเอียดขึ้น
> - Validation → เปรียบเทียบกับ experimental data หรือ analytical solutions

📂 [ไปที่เนื้อหา](CONTENT/06_VALIDATION_AND_VERIFICATION/00_Overview.md)
*   01_V_and_V_Principles.md
*   02_Mesh_Independence.md
*   03_Experimental_Validation.md

### 7. Advanced Topics (หัวข้อขั้นสูง)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain E: Coding/Customization** & **Domain B: Numerics** & **Domain C: HPC**
>
> หัวข้อนี้เชื่อมโยงกับ:
> - **High Performance Computing**:
>   - **Parallel Processing**: ใช้ `decomposePar` (ตามด้วย `decomposeParDict` ใน `system/`) และ `reconstructPar`
>   - **Method**: `scotch`, `metis`, `simple`, `hierarchical`
>   - **Run Command**: `mpirun -np <N> <solver> -parallel`
> - **Advanced Turbulence**:
>   - **LES/DES Models**: ตั้งค่าใน `constant/turbulenceProperties` (เช่น `LESModel`, `DESModel`)
>   - **Inflow Conditions**: ใช้ `turbulentDigitalFilterInlet` หรือ `ATIInflow` boundary conditions
> - **Numerical Methods**:
>   - **Higher-Order Schemes**: ใน `system/fvSchemes` เช่น `Gauss cubic`, `fourth`
>   - **Implicit/Explicit Methods**: ปรับ `ddtSchemes` (เช่น `Euler`, `backward`, `CrankNicolson`)
> - **Multiphysics**:
>   - **FSI (Fluid-Structure Interaction)**: ใช้ solids-based solvers หรือ external coupling
>   - **Custom Solvers**: แก้ไข solver source code ใน `src/` และ compile ด้วย `wmake`
>
> **การนำไปใช้:**
> - HPC → ลดเวลา simulation สำหรับ large cases
> - Advanced models → เพิ่มความแม่นยำสำหรับ flows ที่ซับซ้อน
> - Customization → สร้าง solvers หรือ boundary conditions ที่เฉพาะทาง

📂 [ไปที่เนื้อหา](CONTENT/07_ADVANCED_TOPICS/00_Overview.md)
*   01_High_Performance_Computing.md
*   02_Advanced_Turbulence.md
*   03_Numerical_Methods.md
*   04_Multiphysics.md

---

## 🧭 วิธีการเรียนรู้ (How to Use This Module)
1.  **มือใหม่**: เริ่มต้นจากบทที่ 1 และ 2 เพื่อเข้าใจพื้นฐาน Solver และ Algorithm
2.  **ผู้ใช้งานทั่วไป**: เน้นบทที่ 3 (Turbulence) เพราะเป็นส่วนสำคัญที่สุดในการ setup case ส่วนใหญ่
3.  **งานความร้อน**: ข้ามไปบทที่ 4 หลังจากเข้าใจบทที่ 1-2 แล้ว
