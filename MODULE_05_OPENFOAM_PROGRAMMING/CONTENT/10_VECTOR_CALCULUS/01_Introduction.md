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

## 🎯 Learning Objectives

หลังจากศึกษาบทนี้ คุณจะสามารถ:

1. **อธิบาย** ความหมายทางกายภาพและคณิตศาสตร์ของสี่ตัวดำเนินการพื้นฐาน: Gradient, Divergence, Curl และ Laplacian
2. **ใช้งาน** เนมสเปซ `fvc::` และ `fvm::` อย่างถูกต้องตามบริบทของปัญหา
3. **เลือกใช้** discretization schemes ที่เหมาะสมใน `system/fvSchemes` สำหรับความแม่นยำและความเสถียร
4. **วิเคราะห์** ข้อผิดพลาดจากการใช้ตัวดำเนินการที่ไม่เหมาะสมใน solver ของคุณ
5. **เชื่อมโยง** แคลคูลัสเวกเตอร์กับสมการพื้นฐานใน solvers จริง (เช่น simpleFoam, pimpleFoam)

## 📋 ภาพรวมเนื้อหา (Section Overview)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เชื่อมโยงกับ **Domain B: Numerics & Linear Algebra**
> - **ไฟล์ที่เกี่ยวข้อง:** `system/fvSchemes`, `system/fvSolution`
> - **คีย์เวิร์ด:** `gradSchemes`, `divSchemes`, `laplacianSchemes`, `interpolationSchemes`
> - **การใช้งาน:** การเลือก numerical schemes ที่เหมาะสมสำหรับการคำนวณ gradient, divergence, และ Laplacian บนเมช
> - **โค้ด:** `src/finiteVolume/finiteVolume/fvc/fvcGrad.C`, `src/finiteVolume/finiteVolume/fvm/fvmLaplacian.C`

ส่วนนี้ครอบคลุม **การดำเนินการแคลคูลัสเวกเตอร์** พื้นฐานที่เป็นกระดูกสันหลังทางคณิตศาสตร์ของพลศาสตร์ของไหลเชิงคำนวณ:

- **การดำเนินการ Gradient, Divergence, Curl และ Laplacian**
- **ความแตกต่างระหว่างตัวดำเนินการแบบ Explicit และ Implicit**
- **Discretization schemes ที่ใช้ใน OpenFOAM**

```mermaid
flowchart LR
classDef math fill:#fff9c4,stroke:#fbc02d,color:#000
classDef disc fill:#c8e6c9,stroke:#2e7d32,color:#000
V["Volume Integral: ∫∇·U dV"]:::math -->|Gauss Thm| S["Surface Integral: ∮U·dA"]:::math
S -->|Discretize| Sum["Sum: Σ(Flux · Area)"]:::disc
```
> **Figure 1:** พื้นฐานการคำนวณในวิธีปริมาตรจำกัดที่ใช้ทฤษฎีบทของเกาส์ในการเปลี่ยนรูปแบบอินทิกรัลเชิงปริมาตรให้กลายเป็นการหาผลรวมเชิงพีชคณิตบนหน้าเซลล์ที่คำนวณได้จริง

> [!INFO] **ทางลัดไปคณิตศาสตร์**
> สำหรับพื้นฐานทฤษฎีบทของเกาส์และการ discretization พื้นฐาน ดูได้ที่ **[[00_Overview.md]]** ซึ่งอธิบายรากฐานทางคณิตศาสตร์อย่างละเอียด

## 🔧 การนำไปใช้: เนมสเปซ `fvc::` และ `fvm::` (Implementation Namespaces)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เชื่อมโยงกับ **Domain E: Coding/Customization**
> - **ไฟล์ที่เกี่ยวข้อง:** `src/finiteVolume/finiteVolume/fvc/`, `src/finiteVolume/finiteVolume/fvm/`
> - **คีย์เวิร์ด:** `fvc::grad`, `fvc::div`, `fvm::laplacian`
> - **การใช้งาน:** เรียกใช้ explicit และ implicit operators ใน custom solver
> - **ตัวอย่างไฟล์โค้ด:**
>   - `src/finiteVolume/finiteVolume/fvc/fvcGrad/fvcGrad.C`
>   - `src/finiteVolume/finiteVolume/fvc/fvcDiv/fvcDiv.C`
>   - `src/finiteVolume/finiteVolume/fvm/fvmLaplacian/fvmLaplacian.C`

ใน OpenFOAM การดำเนินการแคลคูลัสเวกเตอร์ถูกนำไปใช้ผ่านสองเนมสเปซหลัก:

### 📊 Explicit vs Implicit

| แง่มุม (Aspect) | **Explicit (`fvc::`)** | **Implicit (`fvm::`)** |
|--------|------------------------|------------------------|
| **การคำนวณ** | การประเมินโดยตรงจากฟิลด์ที่รู้ค่า | การสร้างสัมประสิทธิ์เมทริกซ์ |
| **ผลลัพธ์** | ค่าฟิลด์ (ประเมินทันที) | สมการเมทริกซ์ (ต้องแก้สมการ) |
| **กรณีการใช้งาน** | Post-processing, source terms | Implicit time stepping, steady-state |
| **ความเสถียร** | อาจต้องการ time steps ที่เล็ก | โดยทั่วไปมีความเสถียรสูงกว่า |
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
- **สนามสเกลาร์** → **สนามเวกเตอร์** (ทิศทางที่มีความชันสูงสุด)
- **สนามเวกเตอร์** → **สนามเทนเซอร์** (เทนเซอร์เกรเดียนต์ความเร็ว)

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

**📂 Source:** `applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C`

**📖 คำอธิบาย:** ใน OpenFOAM gradient operator ใช้สำหรับคำนวณการเปลี่ยนแปลงของปริมาณทางฟิสิกส์ในปริภูมิ:
1. **gradP** - คำนวณ pressure gradient ซึ่งเป็นแรงขับเคลื่อนหลักในสมการโมเมนตัม
2. **gradT** - คำนวณ heat flux จาก gradient ของอุณหภูมิ
3. **gradU** - คำนวณ strain rate และ vorticity จาก gradient ของความเร็ว

**🔑 แนวคิดสำคัญ:**
- `volVectorField`: ฟิลด์เวกเตอร์ที่จัดเก็บค่าตรงกลางเซลล์
- `volTensorField`: ฟิลด์เทนเซอร์สำหรับค่า gradient ของฟิลด์เวกเตอร์

---

### 2️⃣ **Divergence** (`∇·φ`)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เชื่อมโยงกับ **Domain B: Numerics & Linear Algebra**
> - **ไฟล์ที่เกี่ยวข้อง:** `system/fvSchemes`
> - **คีย์เวิร์ด:** `divSchemes`
> - **การใช้งาน:** กำหนดวิธีการคำนวณ divergence สำหรับ convection terms
> - **โค้ด:** `src/finiteVolume/finiteVolume/fvc/fvcDiv/fvcDiv.C`

วัดฟลักซ์สุทธิออกจากปริมาตรควบคุม ==สำคัญสำหรับกฎการอนุรักษ์==

$$\nabla \cdot \mathbf{F} = \frac{\partial F_x}{\partial x} + \frac{\partial F_y}{\partial y} + \frac{\partial F_z}{\partial z}$$

**ความหมายทางกายภาพ:**
- **สนามเวกเตอร์** → **สนามสเกลาร์** (ความแรงของแหล่งกำเนิด/จุดดูด)
- **Zero divergence** = การไหลแบบอัดตัวไม่ได้ ($\nabla \cdot \mathbf{U} = 0$)

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

**📂 Source:** `applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`

**📖 คำอธิบาย:** Divergence operator ใช้ตรวจสอบและบังคับใช้กฎการอนุรักษ์:
1. **divU** - ตรวจสอบ mass conservation โดยในกระแส incompressible ค่านี้ควรเป็นศูนย์
2. **divPhi** - คำนวณ momentum flux ผ่านหน้าเซลล์
3. **convTerm** - คำนวณเทอม convection ใน transport equation

**🔑 แนวคิดสำคัญ:**
- `fvc::div()`: Explicit divergence operator ที่ใช้ทฤษฎีบทของเกาส์ในการคำนวณ
- **Conservation laws**: กฎการอนุรักษ์มวล โมเมนตัม และพลังงานถูกบังคับผ่าน divergence operator

---

### 3️⃣ **Curl** (`∇×φ`)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เชื่อมโยงกับ **Domain A: Physics & Fields**
> - **ไฟล์ที่เกี่ยวข้อง:** `system/controlDict` (สำหรับ functionObjects)
> - **คีย์เวิร์ด:** `functionObjects`, `vorticity`, `Q`, `curl`
> - **การใช้งาน:** คำนวณ vorticity และ vortex identification criteria
> - **โค้ด:** `src/finiteVolume/finiteVolume/fvc/fvcCurl/fvcCurl.C`

ประเมินองค์ประกอบการหมุนของสนามเวกเตอร์ จำเป็นสำหรับการวิเคราะห์ vorticity

$$\nabla \times \mathbf{u} = \begin{vmatrix} \mathbf{i} & \mathbf{j} & \mathbf{k} \\ \frac{\partial}{\partial x} & \frac{\partial}{\partial y} & \frac{\partial}{\partial z} \\ u_x & u_y & u_z \end{vmatrix}$$

**ความหมายทางกายภาพ:**
- **สนามเวกเตอร์** → **สนามเวกเตอร์** (แกนการหมุนและขนาด)
- **Zero curl** = การไหลแบบไม่มีการหมุน (potential flow)

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

**📂 Source:** `applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/kineticTheoryModels/kineticTheoryModel/kineticTheoryModel.C`

**📖 คำอธิบาย:** Curl operator ใช้วิเคราะห์การหมุนของกระแส:
1. **vorticity** - คำนวณ vorticity (ω = ∇×U) ซึ่งเป็นเวกเตอร์ที่บอกทิศทางและความเร็วในการหมุน
2. **vorticityMag** - คำนวณขนาดของ vorticity สำหรับการ visualize
3. **Q-criterion** - ระบุโซนที่มีการพัดโดยเปรียบเทียบส่วนประกอบการหมุนกับส่วนประกอบความเครียด

**🔑 แนวคิดสำคัญ:**
- `mag()`: ฟังก์ชันคำนวณขนาดของเวกเตอร์
- `skew()` / `symm()`: แยกส่วนประกอบ antisymmetric (การหมุน) และ symmetric (ความเครียด) ของเทนเซอร์

---

### 4️⃣ **Laplacian** (`∇²φ`)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เชื่อมโยงกับ **Domain B: Numerics & Linear Algebra**
> - **ไฟล์ที่เกี่ยวข้อง:** `system/fvSchemes`, `constant/transportProperties`
> - **คีย์เวิร์ด:** `laplacianSchemes`, `nu`, `DT`, `D`
> - **การใช้งาน:** กำหนดวิธีการคำนวณ Laplacian สำหรับ diffusion terms
> - **โค้ด:** `src/finiteVolume/finiteVolume/fvc/fvcLaplacian/fvcLaplacian.C`, `src/finiteVolume/finiteVolume/fvm/fvmLaplacian/fvmLaplacian.C`

แสดงถึงกระบวนการแพร่ จำเป็นสำหรับการนำความร้อน การไหลหนืด และการแพร่ของมวล

$$\nabla^2 \phi = \nabla \cdot (\nabla \phi) = \frac{\partial^2 \phi}{\partial x^2} + \frac{\partial^2 \phi}{\partial y^2} + \frac{\partial^2 \phi}{\partial z^2}$$

**ความหมายทางกายภาพ:**
- **ฟิลด์ใดๆ** → **ฟิลด์ประเภทเดียวกัน** (diffusion smoothing)
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

**📂 Source:** `applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.H`

**📖 คำอธิบาย:** Laplacian operator ใช้จำลองกระบวนการ diffusion:
1. **laplacianT** - คำนวณ heat conduction ด้วยสัมประสิทธิ์ DT
2. **laplacianU** - คำนวณ viscous diffusion ในสมการโมเมนตัมด้วยสัมประสิทธิ์ความหนืด ν
3. **pEqn** - สร้าง Pressure Poisson equation โดยใช้ implicit Laplacian

**🔑 แนวคิดสำคัญ:**
- `fvc::laplacian()`: Explicit Laplacian operator
- `fvm::laplacian()`: Implicit Laplacian operator ที่สร้างเมทริกซ์สำหรับการแก้สมการ
- `fvScalarMatrix`: เมทริกซ์สมการสเกลาร์ที่ต้องแก้ด้วย linear solver

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

ความแม่นยำและความเสถียรของการดำเนินการ finite volume ขึ้นอยู่กับ **interpolation schemes** ที่ระบุใน `system/fvSchemes`:

### การเปรียบเทียบ Interpolation Schemes

| Scheme | อันดับ | ความแม่นยำ | ความเสถียร | การใช้งานทั่วไป |
|--------|-------|----------|-----------|-------------|
| **Gauss linear** | 2nd | ดี | ปานกลาง | Laminar flow, structured meshes |
| **Gauss upwind** | 1st | ต่ำ | สูงมาก | Turbulent flow, high Reynolds |
| **Gauss limitedLinear** | 2nd (TVD) | ดี | สูง | วัตถุประสงค์ทั่วไป, flows ที่มี shocks |
| **Gauss leastSquares** | 2nd | ดีกว่า | สูง | Unstructured meshes |
| **QUICK** | 3rd | ดีมาก | ต่ำ | การคำนวณที่ต้องการความแม่นยำสูง |

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

**📂 Source:** `applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/ThermalPhaseChangePhaseSystem/ThermalPhaseChangePhaseSystem.C`

**📖 คำอธิบาย:** Discretization schemes กำหนดความแม่นยำและเสถียรภาพของการคำนวณ:
1. **gradSchemes** - กำหนดวิธีคำนวณ gradient: `linear` (2nd order), `leastSquares` (unstructured meshes), `fourth` (ความแม่นยำสูงกว่า)
2. **divSchemes** - กำหนดวิธีคำนวณ divergence: `linearUpwindV` (ผสม scheme), `limitedLinearV` (TVD scheme)
3. **laplacianSchemes** - กำหนดวิธีคำนวณ Laplacian: `corrected` (non-orthogonal correction)

**🔑 แนวคิดสำคัญ:**
- **Gauss theorem**: ฐานของทุก discretization scheme ใน FVM
- **TVD (Total Variation Diminishing)**: Scheme ที่ป้องกัน oscillations ใน flows ที่มี shocks
- **Non-orthogonal correction**: การแก้ไขสำหรับ meshes ที่ไม่ orthogonal

---

## 🎯 ทำไมเรื่องนี้ถึงสำคัญ: มุมมองนักพัฒนา

การเข้าใจว่าเมื่อใดควรใช้ `fvc::grad(p)` เทียบกับ `fvm::laplacian(T)` สามารถสร้างความแตกต่างระหว่าง:

- ✅ **Solver ที่ลู่เข้า (converge) อย่างราบรื่น**
- ❌ **Solver ที่ลู่ออก (diverge) หรือระเบิด**

> [!WARNING] หลุมพรางทั่วไป (Common Pitfall)
> ความเข้าใจผิดเล็กน้อยสามารถนำไปสู่ความล้มเหลวร้ายแรง:
> - การใช้ `fvc::laplacian` แทน `fvm::laplacian` ใน implicit solver
> - การเลือก scheme ที่ไม่เสถียรสำหรับการไหลที่มี Reynolds number สูง
> - การลืมว่า `fvc::` คืนค่า fields ในขณะที่ `fvm::` สร้าง matrices

## 📚 เนื้อหาต่อไป (What's Next)

ในส่วนนี้ เราจะครอบคลุม:

1. **[[02_fvc_vs_fvm|การเปรียบเทียบ fvc vs fvm]]** - เข้าใจความแตกต่างอย่างลึกซึ้ง
2. **[[03_Gradient_Operations|การดำเนินการ Gradient]]** - การคำนวณอนุพันธ์เชิงพื้นที่
3. **[[04_Divergence_Operations|การดำเนินการ Divergence]]** - การบังคับใช้กฎการอนุรักษ์
4. **[[05_Curl_and_Laplacian|การดำเนินการ Curl และ Laplacian]]** - วิเคราะห์การหมุนและการแพร่
5. **[[06_Common_Pitfalls|ข้อควรระวังทั่วไป]]** - วิธีหลีกเลี่ยงข้อผิดพลาดที่พบบ่อย
6. **[[07_Summary_and_Exercises|สรุปและแบบฝึกหัด]]** - ทบทวนความรู้และฝึกฝน

---

## 🧠 Concept Check

<details>
<summary><b>1. Gradient operator ($\nabla \phi$) ทำหน้าที่อะไรและให้ผลลัพธ์เป็นอะไร?</b></summary>

**Gradient** คำนวณ **อัตราการเปลี่ยนแปลงเชิงพื้นที่** ของ field:
- **Scalar field** → **Vector field** (ทิศทางที่มีความชันสูงสุด)
- **Vector field** → **Tensor field** (velocity gradient tensor)

ตัวอย่าง: `fvc::grad(p)` คำนวณ pressure gradient ซึ่งเป็นแรงขับเคลื่อนในสมการโมเมนตัม

</details>

<details>
<summary><b>2. ทำไม zero divergence ($\nabla \cdot U = 0$) จึงสำคัญสำหรับ incompressible flow?</b></summary>

**Zero divergence** หมายความว่า **ปริมาตรของ fluid parcel คงที่** → ของไหลไม่สามารถ compress หรือ expand ได้ในทุกจุด

ใน OpenFOAM:
- ใช้ `fvc::div(U)` ตรวจสอบว่า velocity field สอดคล้องกับ continuity equation
- ค่าที่ไม่เป็นศูนย์หมายถึง **mass conservation error**

</details>

<details>
<summary><b>3. Laplacian operator ($\nabla^2 \phi$) แสดงถึงกระบวนการทางฟิสิกส์อะไร?</b></summary>

**Laplacian** แสดงถึง **diffusion (การแพร่)** — กระบวนการที่ปริมาณกระจายตัวจากที่ที่มีความเข้มข้นสูงไปต่ำ

ตัวอย่าง:
- **Heat conduction:** `fvc::laplacian(DT, T)` → การนำความร้อน
- **Viscous diffusion:** `fvm::laplacian(nu, U)` → ความหนืดในสมการ Navier-Stokes
- **Pressure Poisson:** `fvm::laplacian(rUA, p)` → แก้สมการความดัน

</details>

<details>
<summary><b>4. ความแตกต่างระหว่าง `fvc::` และ `fvm::` คืออะไร?</b></summary>

**`fvc::` (Explicit)**:
- ประเมินค่าทันทีจากฟิลด์ที่รู้ค่า
- คืนค่าฟิลด์ใหม่
- ใช้สำหรับ post-processing, source terms

**`fvm::` (Implicit)**:
- สร้างเมทริกซ์สมการ
- ต้องแก้ระบบสมการเชิงเส้น
- ใช้สำหรับ implicit time stepping, steady-state problems

</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [[00_Overview.md]] — ภาพรวม Vector Calculus
- **บทถัดไป:** [[02_fvc_vs_fvm.md]] — เปรียบเทียบ fvc และ fvm อย่างละเอียด
- **Gradient Operations:** [[03_Gradient_Operations.md]] — การดำเนินการ Gradient