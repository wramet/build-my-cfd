# บทนำสู่แคลคูลัสเวกเตอร์ใน OpenFOAM (Introduction to Vector Calculus in OpenFOAM)

> [!TIP] ทำไมต้องเข้าใจแคลคูลัสเวกเตอร์?
> แคลคูลัสเวกเตอร์คือ **ภาษาของฟิสิกส์** ที่ OpenFOAM ใช้แก้สมการพลศาสตร์ของไหล การเข้าใจ `fvc::grad()`, `fvc::div()`, `fvm::laplacian()` ช่วยให้คุณ:
> - ✅ สร้าง **Custom Solver** ที่เสถียรและแม่นยำ
> - ✅ เขียน **functionObjects** สำหรับคำนวณปริมาณทางฟิสิกส์ (เช่น กำลัง, ฟลักซ์)
> - ✅ Debug การจำลองที่ล้มเหลวจากการเลือก **Numerical Schemes** ที่ไม่เหมาะสม
> - ✅ ปรับแต่ง **Boundary Conditions** ให้ทำงานสอดคล้องกับสมการ
> **ผลลัพธ์:** Simulation ที่ลู่เข้า (converge) เร็วขึ้นและให้ผลลัพธ์ที่เชื่อถือได้

![[calculus_bridge_nabla.png]]

> **Academic Vision:** สะพานที่เชื่อมระหว่างกลุ่มสัญลักษณ์เมฆคณิตศาสตร์นามธรรม (∇, ∇·, ∇²) ไปยังเมช 3 มิติที่เป็นรูปธรรม ในฝั่งเมช สัญลักษณ์จะเปลี่ยนเป็นลูกศรที่ทะลุผ่านหน้าเซลล์ ภาพประกอบทางวิทยาศาสตร์ที่สะอาดตาและงดงาม ใช้ลายเส้นเวกเตอร์ที่ชัดเจน พื้นหลังสีขาว การออกแบบแนวราบ (flat design) กราฟิกเพื่อการศึกษา --อัตราส่วน 16:9

ในพลศาสตร์ของไหลเชิงคำนวณ (CFD) เราทำงานกับสมการที่เต็มไปด้วยตัวดำเนินการทางคณิตศาสตร์ เช่น **$\nabla$** (Nabla/del), **$\nabla^2$** (Laplacian), **$\nabla \cdot$** (divergence), และ **$\nabla \times$** (curl) OpenFOAM แปลงสัญลักษณ์นามธรรมเหล่านี้ให้เป็นฟังก์ชันที่ใช้งานได้จริงผ่านสองเนมสเปซหลัก: **`fvc`** (finite volume calculus - แบบชัดแจ้ง/explicit) และ **`fvm`** (finite volume method - แบบโดยนัย/implicit)

## 📋 ภาพรวมเนื้อหา (Section Overview)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เชื่อมโยงกับ **Domain B: Numerics & Linear Algebra**
> - **ไฟล์ที่เกี่ยวข้อง:** `system/fvSchemes`, `system/fvSolution`
> - **คีย์เวิร์ด:** `gradSchemes`, `divSchemes`, `laplacianSchemes`, `interpolationSchemes`
> - **การใช้งาน:** การเลือก numerical schemes ที่เหมาะสมสำหรับการคำนวณ gradient, divergence, และ Laplacian บนเมช
> - **โค้ด:** `src/finiteVolume/finiteVolume/fvc/fvcGrad.C`, `src/finiteVolume/finiteVolume/fvm/fvmLaplacian.C`

ส่วนนี้ครอบคลุม **การดำเนินการแคลคูลัสเวกเตอร์** พื้นฐานที่เป็นกระดูกสันหลังทางคณิตศาสตร์ของพลศาสตร์ของไหลเชิงคำนวณ:

- **การดำเนินการ Gradient, Divergence, Curl และ Laplacian**
- **วิธีการ Discretization แบบปริมาตรจำกัด (Finite Volume)**
- **ความแตกต่างระหว่างตัวดำเนินการแบบ Explicit และ Implicit**

```mermaid
flowchart LR
classDef math fill:#fff9c4,stroke:#fbc02d,color:#000
classDef disc fill:#c8e6c9,stroke:#2e7d32,color:#000
V["Volume Integral: ∫∇·U dV"]:::math -->|Gauss Thm| S["Surface Integral: ∮U·dA"]:::math
S -->|Discretize| Sum["Sum: Σ(Flux · Area)"]:::disc
```
> **Figure 1:** พื้นฐานการคำนวณในวิธีปริมาตรจำกัดที่ใช้ทฤษฎีบทของเกาส์ในการเปลี่ยนรูปแบบอินทิกรัลเชิงปริมาตรให้กลายเป็นการหาผลรวมเชิงพีชคณิตบนหน้าเซลล์ที่คำนวณได้จริงความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

## 🏗️ รากฐาน: ทฤษฎีบทไดเวอร์เจนซ์ของเกาส์ (The Foundation: Gauss's Divergence Theorem)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เชื่อมโยงกับ **Domain B: Numerics & Linear Algebra**
> - **ไฟล์ที่เกี่ยวข้อง:** `system/fvSchemes`
> - **คีย์เวิร์ด:** `gradSchemes`, `divSchemes`, `laplacianSchemes`
> - **การใช้งาน:** ทฤษฎีบทของเกาส์เป็นพื้นฐานของทุก numerical scheme ใน OpenFOAM การเลือก scheme ที่ถูกต้องขึ้นอยู่กับความแม่นยำและเสถียรภาพที่ต้องการ
> - **โค้ด:** `src/finiteVolume/finiteVolume/fvc/fvcDiv.C`, `src/finiteVolume/finiteVolume/fvc/fvcGrad.C`

OpenFOAM อาศัย **ทฤษฎีบทไดเวอร์เจนซ์ของเกาส์** ในการแปลงอินทิกรัลเชิงปริมาตรของอนุพันธ์ให้เป็นผลรวมฟลักซ์ที่พื้นผิว นี่คือรากฐานสำคัญของวิธีปริมาตรจำกัด (Finite Volume Method - FVM):

![[of_gauss_theorem_visual.png]]
> **Figure 2:** ปริมาตรควบคุม 3 มิติ (เซลล์) พร้อมลูกศรแสดงไดเวอร์เจนซ์ของสนามเวกเตอร์ที่ถูกแปลงเป็นผลรวมของฟลักซ์ผ่านทุกหน้า ภาพประกอบทางวิทยาศาสตร์ที่สะอาดตา

$$\int_V \nabla \cdot \mathbf{U} \, \mathrm{d}V = \oint_A \mathbf{U} \cdot \mathrm{d}\mathbf{A} \approx \sum_f \mathbf{U}_f \cdot \mathbf{S}_f$$

**โดยที่:**
- $V$ = ปริมาตรควบคุม (control volume)
- $A$ = พื้นที่ผิว (surface area)
- $\mathbf{U}_f$ = ค่าที่ถูก interpolate ไปยังหน้า $f$
- $\mathbf{S}_f = \mathbf{n}_f A_f$ = เวกเตอร์พื้นที่หน้า (face area vector) (ปกติ × พื้นที่)
- ผลรวม $\sum_f$ ดำเนินการบนทุกหน้าของเซลล์

กลไกนี้ช่วยให้ OpenFOAM สามารถคำนวณแคลคูลัสบนเมชที่ซับซ้อนได้อย่างแม่นยำในขณะที่ ==รักษาความถูกต้องของกฎการอนุรักษ์อย่างสมบูรณ์ (exactly preserving conservation laws)== ซึ่งเป็นสิ่งสำคัญสำหรับการจำลอง CFD ที่เชื่อถือได้

## 🔧 การนำไปใช้: เนมสเปซ `fvc::` (Implementation: The `fvc::` Namespace)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เชื่อมโยงกับ **Domain E: Coding/Customization**
> - **ไฟล์ที่เกี่ยวข้อง:** `src/finiteVolume/finiteVolume/fvc/`
> - **คีย์เวิร์ด:** `fvc::grad`, `fvc::div`, `fvc::curl`, `fvc::laplacian`
> - **การใช้งาน:** เรียกใช้ explicit operators ใน custom solver หรือ functionObjects
> - **ตัวอย่างไฟล์โค้ด:**
>   - `src/finiteVolume/finiteVolume/fvc/fvcGrad/fvcGrad.C`
>   - `src/finiteVolume/finiteVolume/fvc/fvcDiv/fvcDiv.C`
>   - `src/finiteVolume/finiteVolume/fvc/fvcCurl/fvcCurl.C`
>   - `src/finiteVolume/finiteVolume/fvc/fvcLaplacian/fvcLaplacian.C`

ใน OpenFOAM การดำเนินการแคลคูลัสเวกเตอร์ถูกนำไปใช้ผ่านเนมสเปซ **`fvc::`** สำหรับการคำนวณแบบ **explicit** ตัวดำเนินการเหล่านี้ประเมินเทอมอนุพันธ์โดยตรงโดยใช้ค่าฟิลด์ที่ทราบจาก time step ปัจจุบัน

### 📊 อะไรทำให้ `fvc::` เป็นแบบ Explicit?

ตัวดำเนินการแบบ Explicit (`fvc::`):
- **ประเมินเทอมอนุพันธ์โดยตรง** โดยใช้ค่าฟิลด์ปัจจุบัน
- **ใช้ค่าที่ทราบแล้ว** จากการทำซ้ำ/time step ปัจจุบัน
- **ไม่จำเป็นต้องแก้** ระบบสมการเชิงเส้น
- **จำเป็นสำหรับ**: การ post-processing, การประเมินเทอมต้นทาง (source term), และรูปแบบการอินทิเกรตเวลาแบบ explicit

### 🔍 ความแตกต่างระหว่าง Explicit และ Implicit

> [!INFO] แนวคิดหลัก (Key Concept)
> ความแตกต่างระหว่างตัวดำเนินการ `fvc::` (explicit) และ `fvm::` (implicit) เป็นพื้นฐานของ OpenFOAM:
> - **`fvc::grad(p)`** คืนค่า `volVectorField` ที่มีค่า $\nabla p$ ที่จุดศูนย์กลางเซลล์
> - **`fvm::laplacian(D, T)`** เพิ่มเทอมการแพร่ลงในเมทริกซ์ระบบเพื่อการแก้สมการในภายหลัง

| แง่มุม (Aspect) | **Explicit (`fvc::`)** | **Implicit (`fvm::`)** |
|--------|------------------------|------------------------|
| **การคำนวณ** | การประเมินโดยตรงจากฟิลด์ที่รู้ค่า | การสร้างสัมประสิทธิ์เมทริกซ์ |
| **ผลลัพธ์** | ค่าฟิลด์ (ประเมินทันที) | สมการเมทริกซ์ (ต้องแก้สมการ) |
| **กรณีการใช้งาน** | Post-processing, source terms, explicit time stepping | Implicit time stepping, steady-state problems |
| **ความเสถียร** | อาจต้องการ time steps ที่เล็ก (เงื่อนไข CFL) | โดยทั่วไปมีความเสถียรโดยไม่มีเงื่อนไข |
| **ต้นทุนต่อการประเมิน** | ต่ำ (O(N)) | สูงกว่า (การประกอบเมทริกซ์ + การแก้สมการ) |

## 🎯 สี่ตัวดำเนินการพื้นฐาน (The Four Fundamental Operators)

### 1️⃣ **Gradient** (`∇φ`)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เชื่อมโยงกับ **Domain B: Numerics & Linear Algebra**
> - **ไฟล์ที่เกี่ยวข้อง:** `system/fvSchemes`
> - **คีย์เวิร์ด:** `gradSchemes`
> - **การใช้งาน:** กำหนดวิธีการคำนวณ gradient เช่น `Gauss linear`, `Gauss leastSquares`, `Gauss fourth`
> - **โค้ด:** `src/finiteVolume/finiteVolume/fvc/fvcGrad/fvcGrad.C`

คำนวณอัตราการเปลี่ยนแปลงเชิงพื้นที่ของฟิลด์ เป็นพื้นฐานสำหรับปรากฏการณ์การขนส่ง (transport phenomena)

$$\nabla \phi = \frac{\partial \phi}{\partial x}\mathbf{i} + \frac{\partial \phi}{\partial y}\mathbf{j} + \frac{\partial \phi}{\partial z}\mathbf{k}$$

**ความหมายทางกายภาพ:**
- **สนามสเกลาร์ (Scalar field)** → **สนามเวกเตอร์ (Vector field)** (ทิศทางที่มีความชันสูงสุด)
- **สนามเวกเตอร์ (Vector field)** → **สนามเทนเซอร์ (Tensor field)** (เทนเซอร์เกรเดียนต์ความเร็ว)

**ตัวอย่างโค้ด OpenFOAM:**
```cpp
// Pressure gradient (driving force in momentum equation)
volVectorField gradP = fvc::grad(p);

// Temperature gradient (heat flux calculation)
volVectorField gradT = fvc::grad(T);

// Velocity gradient (strain rate, vorticity)
volTensorField gradU = fvc::grad(U);
```

---

**📂 Source:** `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C`

**📖 คำอธิบาย:** ใน OpenFOAM gradient operator ใช้สำหรับคำนวณการเปลี่ยนแปลงของปริมาณทางฟิสิกส์ในปริภูมิ โดยมีการนำไปใช้ในโค้ดตัวอย่าง 3 แบบ:
1. **gradP** - คำนวณความโน้มถ่วงของความดัน (pressure gradient) ซึ่งเป็นแรงขับเคลื่อนหลักในสมการโมเมนตัม
2. **gradT** - คำนวณการไหลของความร้อน (heat flux) จาก gradient ของอุณหภูมิ
3. **gradU** - คำนวณความเครียดและการหมุน (strain rate และ vorticity) จาก gradient ของความเร็ว

**🔑 แนวคิดสำคัญ:**
- `volVectorField`: ฟิลด์เวกเตอร์ที่จัดเก็บค่าตรงกลางเซลล์ (cell-centered) สำหรับปริมาณเชิงเวกเตอร์
- `volTensorField`: ฟิลด์เทนเซอร์สำหรับค่า gradient ของฟิลด์เวกเตอร์
- `fvc::grad()`: Explicit gradient operator ที่คำนวณค่า gradient จากฟิลด์ที่รู้ค่าในขณะนั้น

---

### 2️⃣ **Divergence** (`∇·φ`)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เชื่อมโยงกับ **Domain B: Numerics & Linear Algebra**
> - **ไฟล์ที่เกี่ยวข้อง:** `system/fvSchemes`
> - **คีย์เวิร์ด:** `divSchemes`
> - **การใช้งาน:** กำหนดวิธีการคำนวณ divergence สำหรับ convection terms เช่น `Gauss linear`, `Gauss upwind`, `Gauss limitedLinearV`
> - **โค้ด:** `src/finiteVolume/finiteVolume/fvc/fvcDiv/fvcDiv.C`

วัดฟลักซ์สุทธิออกจากปริมาตรควบคุม ==สำคัญสำหรับกฎการอนุรักษ์==

$$\nabla \cdot \mathbf{F} = \frac{\partial F_x}{\partial x} + \frac{\partial F_y}{\partial y} + \frac{\partial F_z}{\partial z}$$

**ความหมายทางกายภาพ:**
- **สนามเวกเตอร์ (Vector field)** → **สนามสเกลาร์ (Scalar field)** (ความแรงของแหล่งกำเนิด/จุดดูด)
- **Zero divergence** = การไหลแบบอัดตัวไม่ได้ (incompressible flow) ($\nabla \cdot \mathbf{U} = 0$)

**ตัวอย่างโค้ด OpenFOAM:**
```cpp
// Continuity check (mass conservation)
volScalarField divU = fvc::div(U);

// Momentum flux divergence
volVectorField divPhi = fvc::div(phi);

// Convective term
volScalarField convTerm = fvc::div(phi, T);
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`

**📖 คำอธิบาย:** Divergence operator ใน OpenFOAM ใช้สำหรับตรวจสอบและบังคับใช้กฎการอนุรักษ์ (conservation laws):
1. **divU** - ตรวจสอบการอนุรักษ์มวล (mass conservation) โดยในกระแสที่ไม่บีบอัด (incompressible) ค่านี้ควรเป็นศูนย์
2. **divPhi** - คำนวณการไหลของโมเมนตัม (momentum flux) ผ่านหน้าเซลล์
3. **convTerm** - คำนวณเทอม convection ในสมการขนส่ง (transport equation)

**🔑 แนวคิดสำคัญ:**
- `volScalarField`: ฟิลด์สเกลาร์ที่จัดเก็บค่าตรงกลางเซลล์
- `fvc::div()`: Explicit divergence operator ที่ใช้ทฤษฎีบทของเกาส์ในการคำนวณ
- **Conservation laws**: กฎการอนุรักษ์มวล โมเมนตัม และพลังงานถูกบังคับผ่าน divergence operator

---

### 3️⃣ **Curl** (`∇×φ`)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เชื่อมโยงกับ **Domain A: Physics & Fields** และ **Domain E: Coding/Customization**
> - **ไฟล์ที่เกี่ยวข้อง:** `system/controlDict` (สำหรับ functionObjects)
> - **คีย์เวิร์ด:** `functionObjects`, `vorticity`, `Q`, `curl`
> - **การใช้งาน:** คำนวณ vorticity และ vortex identification criteria สำหรับ post-processing
> - **โค้ด:** `src/finiteVolume/finiteVolume/fvc/fvcCurl/fvcCurl.C`

ประเมินองค์ประกอบการหมุนของสนามเวกเตอร์ จำเป็นสำหรับการวิเคราะห์ vorticity

$$\nabla \times \mathbf{u} = \begin{vmatrix} \mathbf{i} & \mathbf{j} & \mathbf{k} \\ \frac{\partial}{\partial x} & \frac{\partial}{\partial y} & \frac{\partial}{\partial z} \\ u_x & u_y & u_z \end{vmatrix}$$

**ความหมายทางกายภาพ:**
- **สนามเวกเตอร์ (Vector field)** → **สนามเวกเตอร์ (Vector field)** (แกนการหมุนและขนาด)
- **Zero curl** = การไหลแบบไม่มีการหมุน/potential flow

**ตัวอย่างโค้ด OpenFOAM:**
```cpp
// Vorticity calculation
volVectorField vorticity = fvc::curl(U);

// Vorticity magnitude for visualization
volScalarField vorticityMag = mag(vorticity);

// Q-criterion (vortex identification)
volTensorField gradU = fvc::grad(U);
volScalarField Q = 0.5*(magSqr(skew(gradU)) - magSqr(symm(gradU)));
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/kineticTheoryModels/kineticTheoryModel/kineticTheoryModel.C`

**📖 คำอธิบาย:** Curl operator ใช้วิเคราะห์การหมุน (rotation) ของกระแส:
1. **vorticity** - คำนวณ vorticity (ω = ∇×U) ซึ่งเป็นเวกเตอร์ที่บอกทิศทางและความเร็วในการหมุนของฟลูอิด
2. **vorticityMag** - คำนวณขนาด (magnitude) ของ vorticity สำหรับการ visualise โครงสร้างการไหล
3. **Q-criterion** - ใช้ระบุโซนที่มีการพัด (vortex) โดยเปรียบเทียบส่วนประกอบการหมุน (skew) กับส่วนประกอบความเครียด (symm)

**🔑 แนวคิดสำคัญ:**
- `fvc::curl()`: Explicit curl operator ที่คำนวณองค์ประกอบการหมุนของสนามเวกเตอร์
- `mag()`: ฟังก์ชันคำนวณขนาด (magnitude) ของเวกเตอร์
- `skew()` / `symm()`: แยกส่วนประกอบ antisymmetric (การหมุน) และ symmetric (ความเครียด) ของเทนเซอร์

---

### 4️⃣ **Laplacian** (`∇²φ`)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เชื่อมโยงกับ **Domain B: Numerics & Linear Algebra** และ **Domain E: Coding/Customization**
> - **ไฟล์ที่เกี่ยวข้อง:** `system/fvSchemes`, `constant/transportProperties`
> - **คีย์เวิร์ด:** `laplacianSchemes`, `nu`, `DT`, `D`
> - **การใช้งาน:** กำหนดวิธีการคำนวณ Laplacian สำหรับ diffusion terms เช่น `Gauss linear corrected`
> - **โค้ด:** `src/finiteVolume/finiteVolume/fvc/fvcLaplacian/fvcLaplacian.C`, `src/finiteVolume/finiteVolume/fvm/fvmLaplacian/fvmLaplacian.C`

แสดงถึงกระบวนการแพร่ จำเป็นสำหรับการนำความร้อน การไหลหนืด และการแพร่ของมวล

$$\nabla^2 \phi = \nabla \cdot (\nabla \phi) = \frac{\partial^2 \phi}{\partial x^2} + \frac{\partial^2 \phi}{\partial y^2} + \frac{\partial^2 \phi}{\partial z^2}$$

**ความหมายทางกายภาพ:**
- **ฟิลด์ใดๆ (Any field)** → **ฟิลด์ประเภทเดียวกัน (Same type field)** (diffusion smoothing)
- รวมไดเวอร์เจนซ์ของเกรเดียนต์เข้าด้วยกัน

**ตัวอย่างโค้ด OpenFOAM:**
```cpp
// Thermal diffusion (heat conduction)
volScalarField laplacianT = fvc::laplacian(DT, T);

// Viscous diffusion (momentum equation)
volVectorField laplacianU = fvc::laplacian(nu, U);

// Pressure Poisson equation
fvScalarMatrix pEqn(fvm::laplacian(1/rho, p) == fvc::div(U));
```

---

**📂 Source:** `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.H`

**📖 คำอธิบาย:** Laplacian operator ใช้จำลองกระบวนการ diffusion:
1. **laplacianT** - คำนวณการนำความร้อน (heat conduction) ด้วยสัมประสิทธิ์ DT
2. **laplacianU** - คำนวณความหนืด (viscous diffusion) ในสมการโมเมนตัมด้วยสัมประสิทธิ์ความหนืด ν
3. **pEqn** - สร้างสมการ Pressure Poisson โดยใช้ implicit Laplacian (fvm) สำหรับแก้สมการความดัน

**🔑 แนวคิดสำคัญ:**
- `fvc::laplacian()`: Explicit Laplacian operator สำหรับ diffusion terms
- `fvm::laplacian()`: Implicit Laplacian operator ที่สร้างเมทริกซ์สำหรับการแก้สมการ
- `fvScalarMatrix`: เมทริกซ์สมการสเกลาร์ที่ต้องแก้ด้วย linear solver
- **Diffusion processes**: การนำความร้อน, ความหนืด, การแพร่กระจายมวล ล้วนใช้ Laplacian operator

---

## 🔧 โครงร่างการ Discretization (Discretization Schemes)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เชื่อมโยงกับ **Domain B: Numerics & Linear Algebra**
> - **ไฟล์ที่เกี่ยวข้อง:** `system/fvSchemes`
> - **คีย์เวิร์ด:**
>   - `gradSchemes` - สำหรับ gradient calculations
>   - `divSchemes` - สำหรับ convection terms
>   - `laplacianSchemes` - สำหรับ diffusion terms
>   - `interpolationSchemes` - สำหรับ face interpolation
> - **การใช้งาน:** เลือก numerical schemes ที่เหมาะสมกับปัญหา (accuracy vs stability trade-off)
> - **ตัวอย่าง schemes:** `Gauss linear`, `Gauss upwind`, `Gauss limitedLinearV`, `Gauss leastSquares`, `Gauss linear corrected`

ความแม่นยำและความเสถียรของการดำเนินการ finite volume ขึ้นอยู่กับ **interpolation schemes** ที่ระบุใน `system/fvSchemes`:

### การเปรียบเทียบ Interpolation Schemes

| Scheme | อันดับ (Order) | ความแม่นยำ | ความเสถียร | การใช้งานทั่วไป |
|--------|-------|----------|-----------|-------------|
| **Gauss linear** | ที่ 2 | ดี | ปานกลาง | การไหลแบบ Laminar, structured meshes |
| **Gauss upwind** | ที่ 1 | ต่ำ | สูงมาก | การไหลแบบ Turbulent, high Reynolds |
| **Gauss limitedLinear** | ที่ 2 (TVD) | ดี | สูง | วัตถุประสงค์ทั่วไป, การไหลที่มี shocks |
| **Gauss leastSquares** | ที่ 2 | ดีกว่า | สูง | Unstructured meshes |
| **QUICK** | ที่ 3 | ดีมาก | ต่ำ | การคำนวณที่ต้องการความแม่นยำสูง |

**ตัวอย่าง `system/fvSchemes`:**
```cpp
// Define gradient schemes using Gauss theorem with different interpolation
gradSchemes
{
    default         Gauss linear;
    grad(p)         Gauss leastSquares;  // Better on unstructured meshes
    grad(U)         Gauss fourth;        // Higher accuracy
}

// Define divergence schemes for convective terms
divSchemes
{
    default         Gauss linear;
    div(phi,U)      Gauss linearUpwindV grad(U);  // Blended scheme
    div(phi,T)      Gauss limitedLinearV 1;       // TVD scheme
}

// Define Laplacian schemes with non-orthogonal correction
laplacianSchemes
{
    default         Gauss linear corrected;  // Non-orthogonal correction
}
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/ThermalPhaseChangePhaseSystem/ThermalPhaseChangePhaseSystem.C`

**📖 คำอธิบาย:** Discretization schemes กำหนดความแม่นยำและเสถียรภาพของการคำนวณ:
1. **gradSchemes** - กำหนดวิธีคำนวณ gradient โดยใช้ทฤษฎีบท Gauss กับ interpolation ต่างกัน:
   - `linear`: 2nd order, เหมาะกับ laminar flow
   - `leastSquares`: เหมาะกับ unstructured meshes
   - `fourth`: ความแม่นยำสูงกว่า

2. **divSchemes** - กำหนดวิธีคำนวณ divergence สำหรับ convection terms:
   - `linearUpwindV`: ผสม scheme เพื่อสมดุลความแม่นยำและเสถียรภาพ
   - `limitedLinearV`: TVD scheme ป้องกัน oscillations

3. **laplacianSchemes** - กำหนดวิธีคำนวณ Laplacian:
   - `corrected`: ใช้ non-orthogonal correction สำหรับ meshes ที่ไม่ orthogonal

**🔑 แนวคิดสำคัญ:**
- **Gauss theorem**: ฐานของทุก discretization scheme ใน FVM
- **Interpolation**: การประมาณค่าที่ face centers จาก cell centers
- **TVD (Total Variation Diminishing)**: Scheme ที่ป้องกัน oscillations ใน flows ที่มี shocks
- **Non-orthogonal correction**: การแก้ไขสำหรับ meshes ที่ไม่ orthogonal เพื่อรักษาความแม่นยำ

---

## 🎯 ทำไมเรื่องนี้ถึงสำคัญ: มุมมองนักพัฒนา (Why This Matters: The Developer's Perspective)

การเข้าใจว่าเมื่อใดควรใช้ `fvc::grad(p)` เทียบกับ `fvm::laplacian(T)` สามารถสร้างความแตกต่างระหว่าง:

- ✅ **Solver ที่ลู่เข้า (converge) อย่างราบรื่น**
- ❌ **Solver ที่ลู่ออก (diverge) หรือระเบิด**

> [!WARNING] หลุมพรางทั่วไป (Common Pitfall)
> ความเข้าใจผิดเล็กน้อยสามารถนำไปสู่ความล้มเหลวร้ายแรง:
> - การใช้ `fvc::laplacian` แทน `fvm::laplacian` ใน implicit solver
> - การเลือก scheme ที่ไม่เสถียรสำหรับการไหลที่มี Reynolds number สูง
> - การลืมว่า `fvc::` คืนค่า fields ในขณะที่ `fvm::` สร้าง matrices

## 📚 สิ่งที่คุณจะได้เรียนรู้ (What You'll Learn)

ในส่วนนี้ เราจะครอบคลุม:

1. **[[02_fvc_vs_fvm\|การเปรียบเทียบ fvc vs fvm]]** - เข้าใจความแตกต่างอย่างลึกซึ้ง
2. **[[03_Gradient_Operations\|การดำเนินการ Gradient]]** - การคำนวณอนุพันธ์เชิงพื้นที่
3. **[[04_Divergence_Operations\|การดำเนินการ Divergence]]** - การบังคับใช้กฎการอนุรักษ์
4. **[[05_Curl_and_Laplacian\|การดำเนินการ Curl และ Laplacian]]** - วิเคราะห์การหมุนและการแพร่
5. **[[06_Common_Pitfalls\|ข้อควรระวังทั่วไป]]** - วิธีหลีกเลี่ยงข้อผิดพลาดที่พบบ่อย
6. **[[07_Summary_and_Exercises\|สรุปและแบบฝึกหัด]]** - ทบทวนความรู้และฝึกฝน

---

**การเชี่ยวชาญการดำเนินการแคลคูลัสเวกเตอร์เหล่านี้เป็นสิ่งจำเป็นสำหรับการสร้างการจำลอง CFD ที่แม่นยำ เสถียร และมีประสิทธิภาพใน OpenFOAM** แต่ละตัวดำเนินการแปลงกฎทางฟิสิกส์ให้เป็นรูปแบบดิสครีตที่คำนวณได้ ในขณะที่ยังคงรักษาคุณสมบัติการอนุรักษ์พื้นฐานที่ควบคุมพลศาสตร์ของไหล