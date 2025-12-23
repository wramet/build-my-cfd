# การเชื่อมโยงความดัน-ความเร็ว (Pressure-Velocity Coupling)

## 🔍 ภาพรวม (Overview)

**การเชื่อมโยงความดัน-ความเร็ว (Pressure-velocity coupling)** เป็นความท้าทายเชิงตัวเลขที่สำคัญที่สุดใน Computational Fluid Dynamics (CFD) สำหรับการไหลที่อัดตัวไม่ได้ (incompressible flows) เนื่องจากสมการความต่อเนื่อง (continuity equation) ไม่มีพจน์ความดันที่ชัดเจน ความดันจึงทำหน้าที่เป็น "Lagrange multiplier" เพื่อบังคับให้สนามความเร็วเป็นไปตามเงื่อนไข Divergence-free

---

## 📐 รากฐานทางคณิตศาสตร์ (Mathematical Foundation)

### 1.1 ปัญหาการเชื่อมโยง (The Coupling Problem)

สำหรับของไหล Newtonian ที่อัดตัวไม่ได้ (incompressible Newtonian fluids) สมการควบคุมคือ:

**สมการความต่อเนื่อง (การอนุรักษ์มวล):**
$$\nabla \cdot \mathbf{u} = 0$$

**สมการโมเมนตัม (Navier-Stokes):**
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

โดยที่:
- $\mathbf{u}$: เวกเตอร์สนามความเร็ว (velocity vector field) [m/s]
- $p$: สนามความดัน (pressure field) [Pa]
- $\rho$: ความหนาแน่นคงที่ (constant density) [kg/m³]
- $\mu$: ความหนืดพลวัต (dynamic viscosity) [Pa·s]
- $\mathbf{f}$: แรงภายนอก (body forces) [N/m³]

**ความท้าทายพื้นฐาน:**

1. **ความดันปรากฏเป็นเพียง Gradient เท่านั้น** ในสมการโมเมนตัม ($-\nabla p$) → ความดันถูกกำหนดได้ถึงค่าคงที่บวก (additive constant)

2. **ไม่มีสมการความดันที่เป็นอิสระ** สำหรับการไหลที่อัดตัวไม่ได้

3. **ความเร็วต้องเป็นไปตามสมการความต่อเนื่อง** (เงื่อนไข divergence-free) แต่สมการโมเมนตัมเพียงอย่างเดียวไม่สามารถบังคับใช้เงื่อนไขนี้ได้

4. **บน Collocated Grid** หากไม่จัดการอย่างเหมาะสมจะเกิดปัญหา **Checkerboard oscillations**

สิ่งนี้สร้าง **ปัญหาจุดอานม้า (saddle-point problem)**: ความดันทำหน้าที่เป็นตัวคูณ Lagrange (Lagrange multiplier) ที่บังคับใช้ข้อจำกัด divergence-free กับความเร็ว

### 1.2 รูปแบบดิสครีต (Discretized Form)

เมื่อถูกทำให้เป็นดิสครีตโดยใช้วิธี Finite Volume สมการโมเมนตัมที่เซลล์ $P$ จะกลายเป็น:

$$a_P \mathbf{u}_P + \sum_N a_N \mathbf{u}_N = \mathbf{b}_P - (\nabla p)_P$$

โดยที่:
- $a_P$: สัมประสิทธิ์แนวทแยง (รวมส่วนประกอบเชิงเวลาและการพา/การแพร่)
- $a_N$: สัมประสิทธิ์เพื่อนบ้าน
- $\mathbf{b}_P$: เทอมแหล่งกำเนิด (source terms) (ไม่รวมความดัน)

ซึ่งสามารถจัดรูปใหม่ได้เป็น:

$$\mathbf{u}_P = \frac{\mathbf{H}(\mathbf{u})}{a_P} - \frac{1}{a_P} \nabla p$$

โดยที่ $\mathbf{H}(\mathbf{u}) = \frac{\mathbf{b}_P - \sum_N a_N \mathbf{u}_N}{a_P}$ บรรจุเทอมเพื่อนบ้านและเทอมแหล่งกำเนิด

---

## ⚙️ อัลกอริทึมหลักใน OpenFOAM

OpenFOAM นำเสนอสามอัลกอริทึมหลักเพื่อแก้ปัญหาการเชื่อมโยงนี้:

### 2.1 SIMPLE (Semi-Implicit Method for Pressure-Linked Equations)

**วัตถุประสงค์**: สำหรับสภาวะคงที่ (Steady-state)

**กลไก**: ใช้การทำนายโมเมนตัมตามด้วยการแก้ไขความดัน (Pressure Correction)

**ความเสถียร**: จำเป็นต้องใช้ **Under-relaxation** ($\alpha_p \approx 0.3, \alpha_U \approx 0.7$)

**ขั้นตอนอัลกอริทึม:**

1. **การทำนายโมเมนตัม (Momentum Prediction)**: แก้สมการโมเมนตัมโดยใช้สนามความดันที่คาดเดา $p^*$

$$\mathbf{u}_P^* = \mathbf{H}(\mathbf{u}^*) - \frac{1}{a_P}(\nabla p^*)_P$$

2. **การแก้ไขความดัน (Pressure Correction)**: สมการแก้ไขความดันได้มาจากการบังคับใช้ความต่อเนื่อง

$$\nabla \cdot \left( \frac{1}{a_P} \nabla p' \right) = \nabla \cdot \mathbf{u}^*$$

3. **การแก้ไขความเร็ว (Velocity Correction)**: แก้ไขความเร็วโดยใช้การแก้ไขความดัน

$$\mathbf{u}^{n} = \mathbf{u}^* - \frac{1}{a_P}\nabla p'$$
$$p^{n} = p^* + \alpha_p p'$$

```mermaid
flowchart TD
    A["Start with guessed p*, u*"] --> B["Momentum Prediction<br/>Solve a_P u* = H(u) - ∇p*"]
    B --> C["Pressure Correction<br/>Solve ∇·(1/a_P ∇p') = ∇·u*"]
    C --> D["Velocity Correction<br/>u = u* - 1/a_P ∇p'"]
    D --> E["Pressure Update<br/>p = p* + p'"]
    E --> F["Under-Relaxation<br/>Apply α_u, α_p"]
    F --> G{"Converged?"}
    G -->|No| A
    G -->|Yes| H["End"]
```
> **Figure 1:** แผนผังลำดับขั้นตอนของอัลกอริทึม SIMPLE (Semi-Implicit Method for Pressure-Linked Equations) สำหรับการหาผลเฉลยในสภาวะคงที่ (Steady-state) ซึ่งแสดงกระบวนการวนซ้ำตั้งแต่การทำนายโมเมนตัม การแก้ไขความดันและความเร็ว ไปจนถึงการใช้การผ่อนคลาย (Under-relaxation) เพื่อให้ระบบเข้าสู่จุดที่บรรจบกัน

### 2.2 PISO (Pressure-Implicit with Splitting of Operators)

**วัตถุประสงค์**: สำหรับสภาวะชั่วคราว (Transient) ที่ต้องการความแม่นยำเชิงเวลาสูง

**กลไก**: ใช้ขั้นตอน Corrector หลายรอบภายในหนึ่ง Time-step เพื่อรักษา Temporal Accuracy

**ข้อจำกัด**: มักต้องการ $Co < 1$ เพื่อความเสถียร

**ขั้นตอนอัลกอริทึม:**

1. **ขั้นตอนการทำนาย (Predictor Step)**: แก้สมการโมเมนตัมโดยใช้ความดันจาก Time Step ก่อนหน้า $p^n$

2. **ขั้นตอนการแก้ไข (Corrector Steps)**: การแก้ไขความดัน-ความเร็วหลายครั้ง ($k = 1, 2, ..., n_{corr}$)

$$\nabla \cdot \left( \frac{\Delta t}{a_P} \nabla p'^{(k)} \right) = \nabla \cdot \mathbf{u}^{(k)}$$
$$\mathbf{u}^{(k+1)} = \mathbf{u}^{(k)} - \frac{\Delta t}{a_P} \nabla p'^{(k)}$$
$$p^{(k+1)} = p^{(k)} + p'^{(k)}$$

3. **Face Flux Update**: อัปเดต Face Flux $\phi$ เพื่อให้แน่ใจว่ามวลถูกอนุรักษ์

**คุณสมบัติหลัก:**
- **ไม่จำเป็นต้องใช้ under-relaxation** สำหรับขั้นตอนการแก้ไข
- **ขั้นตอนการแก้ไขหลายครั้ง** ช่วยปรับปรุงความแม่นยำเชิงเวลา (temporal accuracy)
- **มีประสิทธิภาพเป็นพิเศษ** สำหรับการไหลแบบชั่วคราว (transient flows) ที่มีช่วงเวลาขนาดเล็ก

### 2.3 PIMPLE (PISO + SIMPLE Hybrid)

**วัตถุประสงค์**: สำหรับสภาวะชั่วคราวที่ต้องการความแข็งแกร่ง (Robustness) สูง

**กลไก**: รวมลูปภายนอก (Outer loops) แบบ SIMPLE เข้ากับลูปภายในแบบ PISO

**จุดเด่น**: สามารถรันด้วย Time-step ขนาดใหญ่ได้ ($Co > 1$)

**โครงสร้าง:**
```
for nOuterCorrectors (SIMPLE-like):
    solve momentum equation
    for nCorrectors (PISO-like):
        pressure correction
        velocity correction
```

```mermaid
flowchart TD
    A[Start time step] --> B[Outer loop: k = 1 to nOuter]
    B --> C[Under-relax momentum solve<br/>with pressure p^k]
    C --> D[Inner PISO loop: i = 1 to nCorr]
    D --> E[Solve pressure correction]
    E --> F[Correct velocity & fluxes]
    F --> G{Inner converged?}
    G -->|No| D
    G -->|Yes| H[Under-relax fields]
    H --> I{Outer converged?}
    I -->|No| B
    I -->|Yes| J[Next time step]
```
> **Figure 2:** แผนผังโครงสร้างของอัลกอริทึม PIMPLE ซึ่งเป็นการผสมผสานระหว่างลูปภายนอกแบบ SIMPLE (Outer loop) และลูปภายในแบบ PISO (Inner loop) เพื่อเพิ่มความเสถียรในการคำนวณสภาวะไม่คงที่ที่มีช่วงเวลาขนาดใหญ่ (Large time steps) โดยอนุญาตให้ค่า Courant number สูงกว่า 1 ได้โดยไม่สูญเสียความแม่นยำทางฟิสิกส์ความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

**ประโยชน์ของ PIMPLE:**
- ความเสถียรสำหรับ time step ขนาดใหญ่
- การลู่เข้าที่แข็งแกร่งสำหรับปัญหา strongly coupled
- ยืดหยุ่นสำหรับทั้งสภาวะคงที่และชั่วคราว

---

## 🛠️ เทคนิคพิเศษใน OpenFOAM

### 3.1 Rhie-Chow Interpolation

เพื่อป้องกันปัญหาสนามความดันแบบตารางหมากรุกบน Collocated Grid OpenFOAM ใช้การประมาณค่าความเร็วที่หน้าเซลล์ ($\mathbf{u}_f$) แบบพิเศษ:

$$\mathbf{u}_f = \overline{\mathbf{u}}_f - \mathbf{D}_f (\nabla p_f - \overline{\nabla p}_f)$$

โดยที่:
- $\overline{\mathbf{u}}_f$ คือความเร็วที่ประมาณค่าในช่วงเชิงเส้น
- $\mathbf{D}_f$ คือเมทริกซ์สัมประสิทธิ์ที่จุดศูนย์กลางหน้าเซลล์
- $\nabla p_f$ คือเกรเดียนต์ความดันที่หน้าเซลล์
- $\overline{\nabla p}_f$ คือเกรเดียนต์ความดันที่ประมาณค่าในช่วง

เทอมที่เพิ่มเข้ามาทำหน้าที่เป็น Numerical Diffusion ที่ช่วยเชื่อมโยงความดันและความเร็วในระดับเซลล์

**OpenFOAM Code Implementation:**
```cpp
// Rhie-Chow interpolation implementation
surfaceScalarField phiU
(
    fvc::interpolate(U, "interpolate(U)") & mesh.Sf()
);

// Pressure gradient correction
surfaceScalarField gradpByA
(
    (fvc::interpolate(rAU)*fvc::snGrad(p))*mesh.magSf()
);

// Final flux calculation
phi = phiU - gradpByA;
```

### 3.2 Non-Orthogonal Correction

สำหรับ Mesh ที่ไม่ตั้งฉาก ($\theta > 0$) OpenFOAM จะทำการวนซ้ำเพื่อแก้ไขความคลาดเคลื่อนของ Laplacian operator

**เกรเดียนต์หน้าเซลล์ที่แก้ไขแล้ว:**
$$\nabla \phi_f \cdot \mathbf{S}_f = \underbrace{\frac{\phi_N - \phi_P}{d_{PN}} |\mathbf{S}_f|}_{\text{orthogonal term}} + \underbrace{\overline{(\nabla \phi)}_f \cdot (\mathbf{S}_f - \mathbf{d}_{PN})}_{\text{non-orthogonal correction}}$$

**OpenFOAM Code Implementation:**
```cpp
while (pimple.correctNonOrthogonal())
{
    fvScalarMatrix pEqn
    (
        fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
    );
    pEqn.solve();
}
```

**แนวทางปฏิบัติที่แนะนำ:**

| คุณภาพ Mesh | จำนวนการแก้ไขที่แนะนำ | เหตุผล |
|-------------|----------------------|---------|
| **ดีเยี่ยม (non-orthogonality < 30°)** | 0-1 ครั้ง | ข้อผิดพลาดต่ำมาก |
| **ดี (30°-60°)** | 1-2 ครั้ง | ข้อผิดพลาดปานกลาง |
| **ยอมรับได้ (60°-70°)** | 2-3 ครั้ง | ต้องการการแก้ไขมากขึ้น |
| **ไม่ดี (> 70°)** | 3+ ครั้งหรือปรับปรุง Mesh | ข้อผิดพลาดสูงมาก |

---

## 📋 สรุปพารามิเตอร์ที่แนะนำ (Recommended Parameters)

| อัลกอริทึม | Pressure Relaxation | Velocity Relaxation | nCorrectors | nOuterCorrectors |
|------------|---------------------|---------------------|-------------|------------------|
| **SIMPLE** | 0.2 - 0.3 | 0.5 - 0.7 | 1 | N/A |
| **PISO** | 1.0 (No relax) | 1.0 (No relax) | 2 - 3 | N/A |
| **PIMPLE** | 0.3 - 0.7 (Outer) | 0.6 - 0.9 (Outer) | Inner: 2 | Outer: 2-5 |

### ตัวอย่างการตั้งค่าใน `fvSolution`

**SIMPLE:**
```cpp
SIMPLE
{
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;

    relaxationFactors
    {
        fields
        {
            p               0.3;
        }
        equations
        {
            U               0.7;
            k               0.7;
            epsilon         0.7;
        }
    }
}
```

**PISO:**
```cpp
PISO
{
    nCorrectors          2;
    nNonOrthogonalCorrectors 0;
    pRefCell             0;
    pRefValue            0;
}
```

**PIMPLE:**
```cpp
PIMPLE
{
    nOuterCorrectors    2;
    nCorrectors         2;
    nNonOrthogonalCorrectors 0;
    pRefCell            0;
    pRefValue           0;

    relaxationFactors
    {
        fields
        {
            p           0.3;
        }
        equations
        {
            U           0.7;
        }
    }
}
```

---

## 🎯 การเลือกอัลกอริทึมที่เหมาะสม

### ตารางการเปรียบเทียบ

| คุณสมบัติ | SIMPLE | PISO | PIMPLE |
|---------|--------|------|---------|
| **ชื่อเต็ม** | Semi-Implicit Method for Pressure-Linked Equations | Pressure-Implicit with Splitting of Operators | Merged PISO-SIMPLE |
| **ความแม่นยำเชิงเวลา** | สภาวะคงที่ (pseudo-time) | Transient อันดับ 2 | อันดับ 1–2 (ขึ้นอยู่กับ outer loops) |
| **Relaxation factors** | จำเป็น (α_u ≈ 0.7, α_p ≈ 0.3) | ไม่มี | Outer: จำเป็น, Inner: ไม่มี |
| **การแก้ไขต่อขั้นตอน** | 1 | 2–4 (nCorrectors) | Outer × Inner (nOuter × nCorr) |
| **ขีดจำกัด Courant number** | ไม่มี (pseudo-time) | Co < 1 โดยทั่วไป | Co > 1 เป็นไปได้ด้วย outer relaxation |
| **เหมาะที่สุดสำหรับ** | Steady RANS, natural convection | LES, DNS, startup transients | Large Time Steps, Moving Mesh, Multiphase |
| **OpenFOAM solver** | `simpleFoam` | `pisoFoam` | `pimpleFoam` |

### แนวทางการเลือก

1. **การไหลเป็นแบบ Steady หรือไม่?** → ใช้ **SIMPLE**
2. **ความแม่นยำเชิงเวลาสำคัญหรือไม่เมื่อใช้ Δt ขนาดเล็ก?** → ใช้ **PISO**
3. **ต้องการ Time Step ขนาดใหญ่หรือฟิสิกส์ที่ซับซ้อนหรือไม่?** → ใช้ **PIMPLE**

### การใช้งานที่แนะนำ

| การใช้งาน | อัลกอริทึมหลัก | เหตุผล |
|-------------|-------------------|-----------|
| **Steady-state aerodynamics** | SIMPLE | มีประสิทธิภาพสูงสุดสำหรับ steady RANS |
| **Transient vortex shedding** | PISO | จับความถี่ได้อย่างแม่นยำ |
| **Multiphase VOF** | PIMPLE | จัดการอัตราส่วนความหนาแน่นขนาดใหญ่ได้ |
| **Moving mesh (FVM)** | PIMPLE | Outer relaxation ทำให้การเคลื่อนที่ของ Mesh เสถียร |
| **Buoyancy-driven flow** | PIMPLE | เชื่อมโยงความดันกับการเปลี่ยนแปลงความหนาแน่น |
| **LES/DNS** | PISO | ความแม่นยำเชิงเวลาเป็นสิ่งสำคัญ |

---

## 📊 การตรวจสอบความลู่เข้า (Convergence Monitoring)

### การตั้งค่า Solver ใน OpenFOAM

```cpp
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-7;
        relTol          0.01;
        smoother        GaussSeidel;
        nPreSweeps      0;
        nPostSweeps     2;
        cacheAgglomeration on;
    }

    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-8;
        relTol          0;
        nSweeps         1;
    }
}
```

### การตรวจสอบการลู่เข้าโดยรวม

```cpp
SIMPLE
{
    converged       false;
    residualControl
    {
        p               1e-6;
        U               1e-5;
        '(k|epsilon|omega)' 1e-5;
    }
}
```

### ตัวบ่งชี้การลู่เข้าทางกายภาพ

| ตัวบ่งชี้ | วิธีการตรวจสอบ | เกณฑ์ที่ยอมรับได้ |
|------------|-------------------|-------------------|
| **การลู่เข้าของแรง/โมเมนตัม** | ตรวจสอบ drag, lift, moment | ΔF/F < 1% |
| **การอนุรักษ์อัตราการไหลเชิงมวล** | เปรียบเทียบอัตราการไหลทางเข้า/ออก | < 1% |
| **การลดลงของความดัน** | ตรวจสอบความแตกต่างของความดัน | คงที่ |

---

## 🔗 การเชื่อมโยงกับไฟล์อื่น ๆ

### การพึ่งพาโดยตรง

**จาก: `../01_INCOMPRESSIBLE_FLOW_SOLVERS/00_Overview.md`**

เนื้อหาเกี่ยวกับการเชื่อมโยงความดัน-ความเร็วนี้สร้างขึ้นโดยตรงบนพื้นฐานของ **Incompressible Flow Solver**

| Solver | Algorithm | ประเภทการจำลอง |
|--------|-----------|------------------|
| **simpleFoam** | SIMPLE algorithm | สภาวะคงที่ (steady-state) |
| **pimpleFoam** | PIMPLE algorithm | สภาวะไม่คงที่พร้อมช่วงเวลาขนาดใหญ่ |
| **icoFoam** | เฉพาะ pressure-velocity coupling | Transient Laminar Flow |

### ความก้าวหน้าต่อไป

**ถึง: `../03_TURBULENCE_MODELING/00_Overview.md`**

กรอบการทำงานการเชื่อมโยงความดัน-ความเร็วเป็น **รากฐานสำหรับการนำ Turbulence Model ไปใช้งาน**

**Reynolds-Averaged Navier-Stokes (RANS):**
$$\frac{\partial \bar{\mathbf{u}}}{\partial t} + \bar{\mathbf{u}} \cdot \nabla \bar{\mathbf{u}} = -\frac{1}{\rho} \nabla \bar{p} + \nu \nabla^2 \bar{\mathbf{u}} - \nabla \cdot \mathbf{R}$$

**ผลกระทบของ Turbulence ต่อ Coupling:**
- **Turbulent Stresses** $\mathbf{R} = \overline{\mathbf{u}' \otimes \mathbf{u}'}$ สร้าง Additional Coupling Terms
- **Modified Pressure** รวมถึง Turbulence Kinetic Energy: $p^* = \bar{p} + \frac{2}{3}\rho k$

---

**หัวข้อถัดไป**: [[01_Mathematical_Foundation.md|รากฐานทางคณิตศาสตร์อย่างละเอียด]]
