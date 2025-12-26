# แนวปฏิบัติที่ดีที่สุด (Best Practices)

## ภาพรวม (Overview)

เอกสารฉบับนี้รวบรวมแนวปฏิบัติที่ดีที่สุดสำหรับการจำลอง CFD ด้วย OpenFOAM โดยครอบคลุมตั้งแต่การเตรียม Mesh การตั้งค่า Numerical Schemes การเลือก Solver ไปจนถึงการตรวจสอบความถูกต้องและการยืนยันผลลัพธ์ แนวปฏิบัติเหล่านี้มีจุดประสงค์เพื่อปรับปรุงความน่าเชื่อถือ ความแม่นยำ และประสิทธิภาพของการจำลอง


```mermaid
graph LR
%% Mind map style
BestPractices["CFD Best Practices"]:::implicit

subgraph Mesh ["Mesh Quality"]
Ortho["Non-Orthogonality < 50°"]:::explicit
Skew["Skewness < 0.5"]:::explicit
end

subgraph Numerics ["Numerics"]
Time["Courant Number < 1"]:::explicit
Schemes["Bounded Schemes for div"]:::implicit
end

subgraph Setup ["Setup"]
BCs["Robust BCs"]:::implicit
Init["Reasonable Initialization"]:::context
end

BestPractices --> Mesh
BestPractices --> Numerics
BestPractices --> Setup

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;
```
> **Figure 1:** กรอบแนวคิดแนวปฏิบัติที่ดีที่สุดสำหรับการจำลอง CFD ครอบคลุมตั้งแต่คุณภาพของ Mesh, แผนการคำนวณเชิงตัวเลข, การตั้งค่า Solver ไปจนถึงการตรวจสอบความถูกต้องและการยืนยันผลลัพธ์


คุณภาพของ Mesh เป็นปัจจัยสำคัญที่ส่งผลต่อความแม่นยำและความเสถียรของการจำลอง CFD คุณภาพ Mesh ที่ไม่ดีอาจทำให้เกิดข้อผิดพลาดเชิงตัวเลข ลดความแม่นยำของ Solution และอาจทำให้การจำลองเกิดการ Divergence ได้

> [!WARNING] ความสำคัญของ Mesh Quality
> Mesh ที่มีคุณภาพต่ำอาจทำให้เกิด:
> - Numerical diffusion ที่สูงขึ้น
> - การคำนวณ Gradient ที่ไม่แม่นยำ
> - การลู่เข้าที่ช้าลงหรือล้มเหลว
> - ผลลัพธ์ทางฟิสิกส์ที่ผิดพลาด

### พารามิเตอร์คุณภาพหลัก

#### **Non-orthogonality**

การวัดมุมระหว่าง Face normal vector และเส้นเชื่อมต่อจุดศูนย์กลางของ Cell ที่อยู่ติดกัน พารามิเตอร์นี้ส่งผลโดยตรงต่อความแม่นยำของการคำนวณ Gradient โดยใช้ Gauss theorem

$$\cos(\theta) = \frac{\mathbf{n}_f \cdot \mathbf{d}_{PN}}{|\mathbf{n}_f| |\mathbf{d}_{PN}|}$$

โดยที่:
- $\mathbf{n}_f$ = Face normal vector
- $\mathbf{d}_{PN}$ = เวกเตอร์เชื่อมต่อระหว่าง Cell Center P และ N
- $\theta$ = Non-orthogonal angle

**ค่าที่แนะนำ:**
- **< 50°**: คุณภาพดี (Good quality)
- **50° - 70°**: ยอมรับได้ (Acceptable)
- **> 70°**: วิกฤต (Critical) อาจเกิด Numerical diffusion ที่สำคัญ

**การควบคุม:**
```cpp
// Pressure solver settings in fvSchemes dictionary
// Non-orthogonal correction iterations improve accuracy for non-orthogonal meshes
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-6;
        relTol          0.1;
        smoother        GaussSeidel;
        nNonOrthogonalCorrectors 2;  // Number of correction iterations
    }
}
```

> **📂 Source:** `.applications/test/patchRegion/cavity_pinched/system/fvSolution`
>
> **คำอธิบาย:** 
> - **Non-orthogonal correctors** ใช้สำหรับปรับปรุงความแม่นยำของการคำนวณ Gradient ใน Mesh ที่ไม่ตั้งฉาก (Non-orthogonal meshes)
> - การทำ correction iterations หลายครั้งช่วยลด error จากการที่ Face normal ไม่ตั้งฉากกับเส้นเชื่อมระหว่าง Cell centers
> - ค่าที่แนะนำ: 0 สำหรับ orthogonal meshes, 1-3 สำหรับ meshes ที่มี non-orthogonality ปานกลาง, 4+ สำหรับกรณีวิกฤต
>
> **แนวคิดสำคัญ:**
> - **Gauss Theorem**: ใช้ในการคำนวณ Gradient บน Mesh surfaces
> - **Non-orthogonal correction**: เทอมที่แก้ไข error จากเรขาคณิต Mesh ที่ไม่สมบูรณ์
> - **Convergence**: การเพิ่ม correctors อาจช่วยให้ลู่เข้าได้ดีขึ้น แต่ใช้เวลาคำนวณมากขึ้น


```mermaid
graph TD
%% Geometric Relation
subgraph Connection ["Cell Connectivity"]
P["Cell P"]:::implicit
N["Cell N"]:::implicit
d["Vector d (P to N)"]:::context
end

subgraph FaceGeometry ["Face Geometry"]
f["Face f"]:::implicit
n["Normal Vector n"]:::explicit
end

subgraph Analysis ["Non-Orthogonality"]
Angle["Angle θ between d and n"]:::explicit
Limit["Limit: θ < 70°"]:::context
Correction["Non-Ortho Correction Required"]:::explicit
end

d --> Angle
n --> Angle
Angle --> Limit
Limit --> Correction

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;
```
> **Figure 2:** การวิเคราะห์ความไม่ตั้งฉาก (Non-orthogonality) ของ Mesh และผลกระทบต่อการคำนวณเกรเดียนต์โดยใช้ทฤษฎีบทของเกาส์ ซึ่งความเบี่ยงเบนที่มากเกินไปจะลดความแม่นยำของผลเฉลยลง


การวัดปริมาณการเบี่ยงเบนของจุด Face-cell intersection จาก Geometric face center

$$\text{Skewness} = \frac{|\mathbf{d}_{Pf} + \mathbf{d}_{fN}|}{|\mathbf{d}_{PN}|}$$

**ค่าที่แนะนำ:**
- **< 0.5**: คุณภาพดี
- **0.5 - 0.6**: ยอมรับได้
- **> 0.6**: วิกฤต สามารถลดความแม่นยำได้อย่างรุนแรง

**ผลกระทบ:**
- นำข้อผิดพลาด Interpolation เข้ามาในการคำนวณ Face value
- ลดความแม่นยำของ Flux calculations
- อาจทำให้เกิดการลู่เข้าที่ไม่ดี

**เครื่องมือวินิจฉัย:**
```bash
# Check mesh quality
checkMesh

# Check only skewness
checkMesh -skew
```

#### พารามิเตอร์คุณภาพเพิ่มเติม

| พารามิเตอร์ | ค่าที่แนะนำ | ผลกระทบหากเกินขีดจำกัด | การวัด |
|--------------|-------------|---------------------|----------|
| **Aspect ratio** | < 10 | ลดความแม่นยำในทิศทางที่ยาว | $\frac{\Delta x_{max}}{\Delta x_{min}}$ |
| **Cell expansion ratio** | < 1.5 | สร้าง Numerical errors | $\frac{\Delta x_{adjacent}}{\Delta x_{current}}$ |
| **Mesh gradation** | ค่อยๆ เปลี่ยน | หากเปลี่ยนแปลงเร็วเกินไป อาจไม่ลู่เข้า | การเปลี่ยนขนาดเซลล์ต่อเนื่อง |
| **Concavity** | < 80° | ปัญหา Interpolation | มุมภายในของเซลล์ |
| **Volume change** | < 20% | Numerical instability | การเปลี่ยนแปลงปริมาตรเซลล์ |

> [!TIP] การเตรียม Mesh ที่ดี
> 1. เริ่มต้นด้วย Structured mesh หากเป็นไปได้
> 2. ใช้ Boundary layer mesh สำหรับปัญหาที่มี Wall shear
> 3. หลีกเลี่ยงการเปลี่ยนขนาดเซลล์ที่รุนแรง
> 4. ตรวจสอบคุณภาพ Mesh ด้วย `checkMesh` ก่อนเริ่ม simulation

---

## การตรวจสอบการลู่เข้า (Convergence Monitoring)

การประเมิน Convergence ใน OpenFOAM โดยทั่วไปเกี่ยวข้องกับการตรวจสอบตัวบ่งชี้หลายตัวที่รวมกันกำหนดความน่าเชื่อถือของ Solution

### **Residuals**

แสดงถึงการวัดว่า Solution ปัจจุบันเป็นไปตาม Discretized governing equations ได้ดีเพียงใด

$$r = |A\phi - b|$$

โดยที่:
- $A$ = Coefficient matrix
- $\phi$ = Solution vector
- $b$ = Source vector

**การตรวจสอบ Residuals:**
```cpp
// Residual monitoring function in controlDict
// Tracks how well the current solution satisfies the discretized equations
functions
{
    residuals
    {
        type            residuals;
        libs            ("libutilityFunctionObjects.so");
        writeResidualFields  no;
        fields          (p U k epsilon);
    }
}
```

> **📂 Source:** `.applications/test/patchRegion/cavity_pinched/system/fvSolution` (for solver configuration context)
>
> **คำอธิบาย:**
> - **Residuals** วัดความผิดพลาดระหว่าง Solution ปัจจุบันกับสมการ Discretized
> - การลดลง 3-6 ระดับขนาด (orders of magnitude) โดยทั่วไปบ่งชี้การลู่เข้าที่ดี
> - Residual target โดยทั่วไป: < 1e-5 สำหรับ solvers ส่วนใหญ่
>
> **แนวคิดสำคัญ:**
> - **Discretized equations**: สมการที่แปลงเป็นรูปแบบพีชคณิตเชิงเส้น
> - **Coefficient matrix**: เมทริกซ์ที่เก็บสัมประสิทธิ์จากการ Discretization
> - **Convergence criteria**: ค่าที่ยอมรับได้สำหรับ residuals เพื่อหยุดการคำนวณ


**เกณฑ์การลู่เข้า:**
- **การลดลงที่ต้องการ**: 3-6 ระดับขนาด (orders of magnitude)
- **เกณฑ์การลู่เข้า**: < 1e-5 สำหรับ Solvers ส่วนใหญ่
- **Steady-state**: Residuals ควรลดลงจนถึง plateau ที่ค่าต่ำ
- **Transient**: Residuals ต่ำกว่า threshold ในแต่ละ time step

### **Under-relaxation**

เทคนิค Stabilization ที่ช่วยชะลออัตราการเปลี่ยนแปลงเพื่อป้องกัน Numerical oscillations และ Divergence

$$\phi^{new} = \phi^{old} + \alpha (\phi^{calc} - \phi^{old})$$

โดยที่:
- $\phi^{new}$ = Updated solution
- $\phi^{old}$ = Previous iteration value
- $\phi^{calc}$ = ค่าที่คำนวณใหม่
- $\alpha$ = Under-relaxation factor (โดยทั่วไป 0.3-0.8)

**การตั้งค่าใน `fvSolution`:**
```cpp
// Under-relaxation factors stabilize iterative solution process
// Controls how much of the newly calculated solution is accepted
relaxationFactors
{
    fields
    {
        p               0.3;    // Pressure: higher relaxation
        U               0.5;    // Velocity: moderate relaxation
        T               0.5;    // Temperature: moderate relaxation
    }
    equations
    {
        k               0.7;    // TKE: lower relaxation
        epsilon         0.7;    // Dissipation: lower relaxation
    }
}
```

> **📂 Source:** `.applications/test/fieldMapping/pipe1D/system/fvSolution` (for similar structure context)
>
> **คำอธิบาย:**
> - **Under-relaxation factors** ควบคุมอัตราการเปลี่ยนแปลงของ Solution ระหว่าง Iterations
> - ค่าต่ำ (0.2-0.4): เสถียรกว่า แต่ลู่เข้าช้ากว่า - เหมาะสำหรับ Pressure
> - ค่าสูง (0.6-0.9): ลู่เข้าเร็วกว่า แต่เสี่ยงต่อ Oscillations - เหมาะสำหรับ Turbulence quantities
>
> **แนวคิดสำคัญ:**
> - **Iterative solution**: การแก้สมการซ้ำๆ จนกว่าจะลู่เข้า
> - **Numerical stability**: การป้องกันการเกิด Oscillations หรือ Divergence
> - **Convergence acceleration**: การปรับค่า Alpha ขณะลู่เข้าเพื่อเร่งการคำนวณ


**คำแนะนำการตั้งค่า:**
- **Steady-state problems**: ใช้การผ่อนปรนสูงกว่า (0.3-0.5)
- **Transient problems**: สามารถใช้การผ่อนปรนต่ำกว่า (0.7-0.9)
- **Highly non-linear**: ลดค่า alpha หากไม่ลู่เข้า
- **Near convergence**: เพิ่มค่า alpha เพื่อเร่งการลู่เข้า

### ตัวบ่งชี้การลู่เข้าเพิ่มเติม

| ตัวบ่งชี้ | คำอธิบาย | เกณฑ์ |
|------------|-----------|--------|
| **Mass balance** | Net mass flux ที่ boundaries | < 1% ของ inlet mass flow |
| **Force convergence** | Forces บน surfaces ที่สนใจ | < 1% change ใน 50 iterations |
| **Field monitoring** | ค่าที่จุดเฝ้าสังเกต | ค่าคงที่หรือ oscillate น้อย |
| **Global quantities** | Integrated quantities (lift, drag) | ค่าคงที่หรือ trend ชัดเจน |

---

## การเลือก Numerical Scheme (Numerical Scheme Selection)

### **Temporal Discretization Schemes**

| Scheme | ลำดับความแม่นยำ | รูปแบบสมการ | ความเสถียร | กรณีที่เหมาะสม |
|--------|-----------------|--------------|-------------|----------------|
| **Euler** | First-order explicit | $\phi^{n+1} = \phi^n + \Delta t \cdot f(\phi^n)$ | Conditionally stable (CFL < 1) | การทดสอบเบื้องต้น, Simple problems |
| **Backward** | Second-order implicit | $\frac{3\phi^{n+1} - 4\phi^n + \phi^{n-1}}{2\Delta t}$ | Unconditionally stable | การจำลอง Transient ทั่วไป, Large time steps |
| **CrankNicolson** | Second-order | $\frac{\phi^{n+1} - \phi^n}{\Delta t} = \frac{1}{2}[f(\phi^n) + f(\phi^{n+1})]$ | Good stability | การจำลองที่ต้องการความแม่นยำสูง |
| **BDF2** | Second-order | $\phi^{n+1} = \frac{4}{3}\phi^n - \frac{1}{3}\phi^{n-1} + \frac{2}{3}\Delta t \cdot f(\phi^{n+1})$ | Good stability | High accuracy transient, Stiff problems |

**การตั้งค่าใน `fvSchemes`:**
```cpp
// Time discretization scheme selection
// Controls temporal accuracy and stability characteristics
ddtSchemes
{
    default         backward;  // Options: Euler, backward, CrankNicolson
}
```

> **📂 Source:** Standard OpenFOAM `fvSchemes` dictionary structure
>
> **คำอธิบาย:**
> - **Temporal schemes** กำหนดวิธีการ Discretize อนุพันธ์เชิงเวลา (∂/∂t)
> - **Euler explicit**: ง่ายแต่ต้องการ Time step เล็กมาก (CFL < 1)
> - **Backward implicit**: เสถียรกว่า สามารถใช้ Time step ใหญ่กว่าได้
> - **CrankNicolson**: สมดุลระหว่างความแม่นยำและเสถียรภาพ (Second-order)
>
> **แนวคิดสำคัญ:**
> - **CFL condition**: เกณฑ์ความเสถียรสำหรับ Explicit schemes
> - **Implicit vs Explicit**: การแก้สมการที่ใช้ค่าจาก Time step ถัดไปหรือปัจจุบัน
> - **Order of accuracy**: ลำดับของความแม่นยำตามการขยาย Taylor series


**คำแนะนำ:**
- **Explicit Euler**: เฉพาะการทดสอบเบื้องต้น เนื่องจากต้องการ time step เล็กมาก
- **Implicit Euler**: สำหรับ steady-state และ transient ทั่วไป
- **CrankNicolson**: เมื่อต้องการความแม่นยำสูง แต่ระวัง oscillations
- **BDF2**: สำหรับ transient ที่ต้องการความแม่นยำสูงและ stability ดี

### **Spatial Discretization for Convective Terms**

| Scheme | รูปแบบสมการ | ความแม่นยำ | ข้อดี | ข้อเสีย | กรณีที่เหมาะสม |
|--------|--------------|-------------|--------|---------|----------------|
| **Gauss linear** | $\phi_f = 0.5(\phi_P + \phi_N)$ | Order 2 | Second-order accurate | ไม่เสถียรสำหรับ Reynolds สูง, $Pe > 2$ | Laminar flow, Fine meshes |
| **Gauss upwind** | $\phi_f = \phi_P$ if $\Phi_f > 0$ | Order 1 | Stability สูงมาก | Numerical diffusion สูง | High convection, Coarse meshes |
| **Gauss limitedLinear** | $\phi_f = \phi_P + \psi(r) \cdot \frac{1}{2}(\phi_N - \phi_P)$ | Order 2 | สมดุลระหว่าง accuracy และ stability | Complex implementation | General CFD applications |
| **Gauss vanLeer** | Van Leer limiter | Order 2 | สมดุลดี | Computational cost สูง | Compressible flows, Shocks |
| **Gauss QUICK** | $\frac{6}{8}\phi_P + \frac{3}{8}\phi_N - \frac{1}{8}\phi_{NN}$ | Order 3 | Excellent accuracy | Can be unstable | Structured grids, Smooth flows |

**OpenFOAM Code Implementation:**
```cpp
// Convection scheme selection in fvSchemes
// Uses TVD (Total Variation Diminishing) limiters for stability
divSchemes
{
    div(phi,U)      Gauss limitedLinearV 1;    // Velocity: TVD
    div(phi,k)      Gauss limitedLinear 1;     // TKE: TVD
    div(phi,epsilon) Gauss upwind;             // Dissipation: Upwind
    div(phi,T)      Gauss linear;              // Temperature: Central
}
```

> **📂 Source:** Standard OpenFOAM `fvSchemes` dictionary
>
> **คำอธิบาย:**
> - **Gauss theorem** ใช้ในการแปลง Divergence เป็น Surface integral
> - **limitedLinearV**: TVD limiter ที่ป้องกัน Oscillations ใกล้ Discontinuities
> - **Upwind**: ใช้ค่าจาก Upstream cell - เสถียรแต่มี Numerical diffusion
>
> **แนวคิดสำคัญ:**
> - **Peclet number (Pe)**: อัตราส่วนระหว่าง Convection และ Diffusion
> - **Numerical diffusion**: Error ที่เกิดจากการใช้ Scheme ลำดับต่ำ
> - **TVD limiters**: ฟังก์ชันที่จำกัด Gradient เพื่อป้องกัน Oscillations


**คำแนะนำการเลือก Scheme:**

```mermaid
graph TD
%% Decision Tree
Pe{"Peclet Number (Pe)"}:::context

subgraph DiffusionDominated ["Pe < 2 (Diffusion Dominated)"]
Central["Central Differencing"]:::implicit
Acc["High Accuracy"]:::context
end

subgraph Balanced ["2 < Pe < 10"]
TVD["TVD / Limited Linear"]:::implicit
Stab["Balanced Stability"]:::context
end

subgraph ConvectionDominated ["Pe > 10 (Convection Dominated)"]
Upwind["Upwind"]:::explicit
Diss["Dissipative / Stable"]:::context
end

Pe --> DiffusionDominated
Pe --> Balanced
Pe --> ConvectionDominated

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;
```
> **Figure 3:** แผนผังการตัดสินใจสำหรับการเลือกแผนการคำนวณการพา (Convection scheme) ตามเลขเพกเลต์ ($Pe$) เพื่อรักษาสมดุลระหว่างความแม่นยำและเสถียรภาพตามลักษณะการไหล


| Scheme | คำอธิบาย | ความแม่นยำ | กรณีที่เหมาะสม | Computational Cost |
|--------|------------|-------------|-----------------|-------------------|
| **Gauss linear** | Standard linear interpolation พร้อม Correction | Order 2 | Orthogonal meshes ส่วนใหญ่ | ต่ำ |
| **leastSquares** | Least squares reconstruction | Order 2+ | Complex meshes | สูง |
| **fourthOrder** | Fourth-order accurate | Order 4 | Structured meshes | สูงมาก |

**การตั้งค่าใน `fvSchemes`:**
```cpp
// Gradient calculation method selection
// Determines how cell-to-face gradients are computed
gradSchemes
{
    default         Gauss linear;  // Standard scheme with correction
    // Or for higher accuracy on complex meshes:
    // default         leastSquares;
}
```

> **📂 Source:** Standard OpenFOAM `fvSchemes` dictionary
>
> **คำอธิบาย:**
> - **Gauss linear**: ใช้ Gauss theorem พร้อม Linear interpolation correction
> - **leastSquares**: ใช้ Least squares method เพื่อหา Gradient บน Complex meshes
> - **Non-orthogonal correction**: เทอมเพิ่มเติมสำหรับ Meshes ที่ไม่ตั้งฉาก
>
> **แนวคิดสำคัญ:**
> - **Gauss theorem**: แปลง Volume integral เป็น Surface integral
> - **Gradient reconstruction**: การคำนวณ Gradient จาก Cell values
> - **Mesh sensitivity**: ความแม่นยำขึ้นกับคุณภาพ Mesh และ Orthogonality


**Non-Orthogonal Correction:**
สำหรับ meshes ที่ไม่ orthogonal อย่างสิ้นเชิง:

$$(\nabla \phi)_f \cdot \mathbf{S}_f = |\mathbf{S}_f| \frac{\phi_N - \phi_P}{|\mathbf{d}_{PN}|} + \underbrace{(\nabla \phi)_{correct} \cdot (\mathbf{S}_f - \mathbf{d}_{PN} \frac{|\mathbf{S}_f|}{|\mathbf{d}_{PN}|})}_{\text{Non-orthogonal correction}}$$

การควบคุมจำนวน correction iterations:
```cpp
// Increase corrections for high non-orthogonality
solvers
{
    p
    {
        nNonOrthogonalCorrectors 2;  // Add for high non-orthogonality
    }
}
```

---

## การปรับแต่งการตั้งค่า Solver (Solver Settings Optimization)

### **การเลือก Linear Solver**

| Solver | เหมาะสำหรับ | ข้อดี | ข้อเสีย | Preconditioners |
|--------|---------------|---------|---------|----------------|
| **GAMG** | Large systems ที่มีการเปลี่ยนแปลง Coefficient ราบรื่น | ความเร็วสูงสำหรับ Mesh ใหญ่, Excellent scaling | Memory intensive, Complex setup | DIC, GaussSeidel |
| **PCG** | Symmetric positive definite matrices | Efficient สำหรับ Diffusion equations, Robust | จำกัดกับ symmetric systems | DIC, Cholesky |
| **PBiCGStab** | Non-symmetric systems | Flexible สำหรับ Convection-diffusion, Good stability | อาจต้องการ precondioners | DILU, FDILU |
| **GMRES** | Highly Non-Symmetric, Ill-conditioned | Excellent for difficult systems | Memory usage increases with iterations | DILU, ILU |
| **smoothSolver** | Simple problems | Memory usage ต่ำ, Simple | Convergence ช้าสำร้าง Complex systems | GaussSeidel, DIC |

**การตั้งค่า Tolerance:**
```cpp
// Linear solver configuration for different field variables
// Pressure uses GAMG for efficiency, velocity uses PBiCGStab for stability
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-6;      // Absolute tolerance
        relTol          0.1;       // Relative tolerance (10%)
        smoother        GaussSeidel;
        nPreSweeps      0;
        nPostSweeps     2;
        nFinestSweeps   2;
        cacheAgglomeration on;
        agglomerator    faceAreaPair;
        mergeLevels     1;
    }

    U
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-5;
        relTol          0;         // Tight tolerance
        minIter         0;
        maxIter         1000;
    }

    k
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-6;
        relTol          0.1;
    }

    epsilon
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-6;
        relTol          0.1;
    }
}
```

> **📂 Source:** `.applications/test/patchRegion/cavity_pinched/system/fvSolution`
>
> **คำอธิบาย:**
> - **GAMG** (Geometric-Algebraic Multi-Grid): เหมาะสำหรับ Pressure equation ที่เป็น Elliptic
> - **PBiCGStab** (Stabilized Bi-Conjugate Gradient): สำหรับ Non-symmetric systems เช่น Velocity
> - **Tolerance**: Absolute tolerance คือค่า target, Relative tolerance คือ % การลดลงต่อ iteration
>
> **แนวคิดสำคัญ:**
> - **Preconditioner**: Matrix transformation เพื่อเร่งการลู่เข้า
> - **Multi-grid methods**: ใช้ Multiple grid resolutions สำหรับการแก้ปัญหา
> - **Convergence criteria**: เกณฑ์ที่ตัดสินใจว่า Solution ลู่เข้าแล้ว


**คำแนะนำการตั้งค่า:**
- **Pressure (p)**: ใช้ GAMG สำหรับ meshes ใหญ่, PCG สำหรับ meshes เล็ก
- **Velocity (U)**: PBiCGStab หรือ GMRES สำหรับ convection-dominated flows
- **Turbulence (k, epsilon)**: PBiCGStab หรือ smoothSolver
- **Scalars (T, species)**: เลือกตาม symmetry ของ equation

**Tolerance Guidelines:**

| ตัวแปร | Absolute Tolerance | Relative Tolerance | คำอธิบาย |
|---------|-------------------|-------------------|-----------|
| **Pressure** | 1e-6 to 1e-8 | 0.01 - 0.1 | ต้องความแม่นยำสูง |
| **Velocity** | 1e-5 to 1e-6 | 0 - 0.1 | Tight tolerance สำคัญ |
| **Turbulence** | 1e-6 | 0.1 | Moderate tolerance |
| **Scalars** | 1e-6 to 1e-7 | 0.01 - 0.1 | ขึ้นกับความ sensitivity |

> [!TIP] การเพิ่มประสิทธิภาพ Solver
> 1. เริ่มต้นด้วย tolerances หลวมๆ สำหรับ initial iterations
> 2. ค่อยๆ ผูก tolerances ขณะ approach convergence
> 3. ใช้ `solverPerformance` function object เพื่อตรวจสอบ
> 4. ปรับจำนวน iterations สูงสุดตามความจำเป็น

---

## การใช้งาน Boundary Condition (Boundary Condition Implementation)

### **Wall Boundaries**

**Velocity:**
- **No-slip conditions**: $\mathbf{u} = 0$ (สำหรับ viscous flows)
- **Slip conditions**: $(\mathbf{u} \cdot \mathbf{n}) = 0$ (สำหรับ inviscid flows)

**Thermal:**
- **Fixed temperature**: `fixedValue`
- **Heat flux**: `fixedGradient`
- **Convection**: `externalWallHeatFlux`

**Turbulence Wall Functions:**

| Wall Function | การใช้งาน | $y^+$ range | คำอธิบาย |
|---------------|-------------|------------|-----------|
| **kqRWallFunction** | จัดการ Turbulence kinetic energy | 30 < $y^+$ < 300 | Standard wall function |
| **nutkWallFunction** | จัดการ Turbulent viscosity | 30 < $y^+$ < 300 | $\mu_t = \kappa y u_\tau$ |
| **epsilonWallFunction** | ควบคุม Dissipation rate | 30 < $y^+$ < 300 | $\varepsilon = \frac{u_\tau^3}{\kappa y}$ |
| **omegaWallFunction** | จัดการ Specific dissipation | All $y^+$ | Low-Reynolds compatible |

**ตัวอย่างการตั้งค่า:**
```cpp
// Wall boundary conditions for velocity field
// No-slip condition: velocity is zero at stationary walls
// 0/U
wall
{
    type            noSlip;  // Or fixedValue
    value           uniform (0 0 0);
}

// Wall thermal conditions
// Supports fixed temperature, fixed flux, or convective conditions
// 0/T
wall
{
    type            fixedValue;     // Fixed temperature
    value           uniform 300;

    // Or
    type            fixedGradient;   // Fixed heat flux
    gradient        uniform 100;

    // Or
    type            externalWallHeatFlux;
    mode            coefficient;
    hCoefficient    uniform 10;
    Ta              uniform 300;
}

// Turbulence kinetic energy at wall
// Wall function handles near-wall turbulence behavior
// 0/k
wall
{
    type            kqRWallFunction;
    value           uniform 0;
}

// Dissipation rate or specific dissipation at wall
// Wall function controls near-wall dissipation
// 0/epsilon or 0/omega
wall
{
    type            epsilonWallFunction;  // Or omegaWallFunction
    value           uniform 0;
}
```

> **📂 Source:** Standard OpenFOAM boundary condition setup
>
> **คำอธิบาย:**
> - **No-slip condition**: Fluid velocity เป็นศูนย์ที่ผนัง (วาสคิวลาร์ฟลูว์)
> - **Wall functions**: ใช้สำหรับจำลอง Turbulent boundary layer โดยไม่ต้อง Mesh ละเอียดมาก
> - **$y^+$**: Dimensionless wall distance - 30-300 สำหรับ Standard wall functions
>
> **แนวคิดสำคัญ:**
> - **Boundary layer**: ชั้นของ Fluid ที่ผนังที่ Viscosity effects สำคัญ
> - **Logarithmic law of the wall**: ความสัมพันธ์ระหว่าง Velocity และ Distance from wall
> - **Near-wall meshing**: ความละเอียดของ Mesh ใกล้ผนังสำคัญมาก


### **Inlet Boundaries**

| Boundary Condition | การใช้งาน | ตัวอย่าง Code | หมายเหตุ |
|--------------------|-------------|-----------------|----------|
| **fixedValue** | กำหนดค่าที่แน่นอน | `inlet { type fixedValue; value uniform 10; }` | ง่ายที่สุด, Constant values |
| **fixedGradient** | ระบุค่า Gradient | `inlet { type fixedGradient; gradient uniform 0; }` | Zero-gradient inlet |
| **timeVaryingMappedFixedValue** | Map จาก External data | `inlet { type timeVaryingMappedFixedValue; ... }` | Transient profiles |
| **turbulentInlet** | แนะนำ Turbulent fluctuations | `inlet { type turbulentInlet; ... }` | Realistic turbulence |
| **surfaceFilm** | Film inlet | `inlet { type surfaceFilm; ... }` | Thin film flows |

**ตัวอย่าง Velocity Inlet:**
```cpp
// Simple uniform velocity inlet
// 0/U
inlet
{
    type            fixedValue;
    value           uniform (10 0 0);  // m/s in x-direction
}

// Or with a parabolic profile using coded boundary condition
// 0/U
inlet
{
    type            codedFixedValue;
    value           uniform (0 0 0);
    code
    #{
        vectorField& inletField = *this;

        // Parabolic profile
        scalar y = this->patch().Cf().component(1);
        scalar Umax = 10.0;
        scalar H = 1.0;

        forAll(inletField, i)
        {
            inletField[i] = vector(Umax * 4.0 * y[i] * (H - y[i]) / sqr(H), 0, 0);
        }
    #};
}
```

> **📂 Source:** Standard OpenFOAM inlet boundary conditions
>
> **คำอธิบาย:**
> - **fixedValue**: กำหนดค่าคงที่ที่ Inlet - เหมาะสำหรับ Uniform inflow
> - **codedFixedValue**: ใช้ C++ code เพื่อสร้าง Profile ที่ซับซ้อน
> - **Parabolic profile**: Velocity profile แบบ Fully developed flow
>
> **แนวคิดสำคัญ:**
> - **Boundary layer development**: การพัฒนาของ Boundary layer จาก Inlet
> - **Velocity profile**: การกระจาย Velocity ผ่าน Cross-section
> - **Turbulence specification**: การกำหนด Turbulence quantities ที่ Inlet


### **Outlet Boundaries**

| Boundary Condition | คำอธิบาย | เหมาะสำหรับ | ตัวอย่าง |
|--------------------|------------|-------------|-----------|
| **zeroGradient** | $\nabla \phi = 0$ | Fully developed flows | `outlet { type zeroGradient; }` |
| **inletOutlet** | สลับระหว่าง Inlet/Outlet | การไหลย้อนกลับที่เป็นไปได้ | `outlet { type inletOutlet; inletValue uniform 0; value uniform 0; }` |
| **outletInlet** | คล้าย inletOutlet | การระบุย้อนกลับ | `outlet { type outletInlet; outletValue uniform 0; value uniform 0; }` |
| **pressureInletOutletVelocity** | Pressure-driven | Transient กับ backflow | `outlet { type pressureInletOutletVelocity; value uniform (0 0 0); }` |

**ตัวอย่าง Pressure Outlet:**
```cpp
// Pressure outlet with zero gauge pressure
// 0/p
outlet
{
    type            fixedValue;
    value           uniform 0;  // Gauge pressure = 0
}

// Velocity outlet that handles backflow
// Switches to inlet condition if flow reverses
// 0/U
outlet
{
    type            pressureInletOutletVelocity;
    value           uniform (0 0 0);
}

// Scalar outlet with backflow handling
// 0/T
outlet
{
    type            inletOutlet;
    inletValue      uniform 300;
    value           uniform 300;
}
```

> **📂 Source:** Standard OpenFOAM outlet boundary conditions
>
> **คำอธิบาย:**
> - **zeroGradient**: สมมติว่า Flow พัฒนาเต็มที่ (Fully developed) ที่ Outlet
> - **pressureInletOutletVelocity**: จัดการ Backflow โดยการสลับเป็น Inlet condition
> - **Backflow**: การไหลย้อนกลับที่อาจเกิดขึ้นใน Transient simulations
>
> **แนวคิดสำคัญ:**
> - **Fully developed flow**: Flow ที่ไม่เปลี่ยนแปลงในทิศทางการไหล
> - **Convective outlet**: อนุญาตให้ Fluid ไหลออกโดยไม่มี Reflections
> - **Wave reflection**: ปัญหาที่เกิดจาก Boundary conditions ที่ไม่เหมาะสม


---

## ประสิทธิภาพการคำนวณ (Computational Efficiency)

### **Parallel Computing**

**ขั้นตอนการดำเนินการ:**

```bash
# Decompose case for parallel execution
decomposePar -force

# Run parallel simulation
mpirun -np 4 solver -case . -parallel

# Reconstruct results
reconstructPar

# Or reconstruct only latest time directory
reconstructPar -latestTime
```


```mermaid
graph TD
%% Decomposition
Domain["Global Domain"]:::implicit

subgraph Decomp ["Decomposition"]
Proc0["Processor 0"]:::explicit
Proc1["Processor 1"]:::explicit
Proc2["Processor 2"]:::explicit
Proc3["Processor 3"]:::explicit
end

subgraph Comm ["Communication"]
MPI["MPI Boundaries<br/>(Halo Cells)"]:::context
end

Domain --> Decomp
Proc0 <--> MPI
Proc1 <--> MPI
Proc2 <--> MPI
Proc3 <--> MPI

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;
```
> **Figure 4:** ขั้นตอนการทำงานของการคำนวณแบบขนานผ่านการแบ่งโดเมน (Domain decomposition) แสดงการแยกส่วน Mesh ไปยังตัวประมวลผลต่าง ๆ และการสื่อสารผ่าน MPI เพื่อรวมผลลัพธ์กลับมาเป็นโดเมนที่สมบูรณ์


```cpp
// Domain decomposition configuration
// Controls how the computational domain is split among processors
method          scotch;  // Options: scotch, hierarchical, simple, manual

numberOfSubdomains 4;

scotchCoeffs
{
    // Optional processor weights for load balancing
    processorWeights
    (
        1
        1
        1
        1
    );
}

// Hierarchical method for structured decompositions
hierarchicalCoeffs
{
    n           (4 1 1);  // 4 in x, 1 in y, 1 in z
    delta       0.001;
    order       xyz;
}
```

> **📂 Source:** `.applications/test/patchRegion/cavity_pinched/system/decomposeParDict`
>
> **คำอธิบาย:**
> - **Scotch**: Graph-based decomposition algorithm ที่ให้ Load balancing ที่ดี
> - **Hierarchical**: แบ่งตามทิศทาง (x, y, z) - เหมาะสำหรับ Structured meshes
> - **Processor weights**: กำหนด Load ต่อ Processor สำหรับ Heterogeneous systems
>
> **แนวคิดสำคัญ:**
> - **Domain decomposition**: การแบ่ง Mesh เป็น Subdomains สำหรับ Parallel processing
> - **Load balancing**: การกระจาย Workload ให้สม่ำเสมอทุก Processor
> - **MPI communication**: การแลกเปลี่ยนข้อมูลระหว่าง Processors ที่ Interface boundaries


**คำแนะนำ Parallelization:**
- **Load balancing**: ใช้ `scotch` หรือ `metis` สำหรับ automatic balancing
- **Number of processors**: 10,000 - 100,000 cells per processor
- **Scaling efficiency**: Monitor speedup และ parallel efficiency
- **Memory consideration**: ตรวจสอบ memory per node

### **Memory Optimization**

**เทคนิคการจัดการ Memory:**

```cpp
// Efficient field declaration and temporary usage
// Proper memory management reduces computational overhead

// 1. Appropriate field type selection
volScalarField p(mesh);      // Correct: Scalar field
volVectorField U(mesh);      // Correct: Vector field

// 2. Smart pointers for large objects
autoPtr<volScalarField> pPtr(new volScalarField(mesh));
tmp<volScalarField> tGradP = fvc::grad(p);

// 3. Avoid unnecessary storage
// Do not store intermediate values unnecessarily
// Use expression templates for operations
```

> **📂 Source:** Standard OpenFOAM coding practices
>
> **คำอธิบาย:**
> - **volScalarField**: Field สำหรับ Scalar quantities (Pressure, Temperature)
> - **volVectorField**: Field สำหรับ Vector quantities (Velocity)
> - **autoPtr**: Smart pointer สำหรับ Dynamic memory management
> - **tmp<T>()**: Temporary field ที่ Auto-delete เมื่อไม่ใช้
>
> **แนวคิดสำคัญ:**
> - **Memory allocation**: การจอง Memory สำหรับ Fields และ Matrices
> - **Memory leaks**: การไม่คืน Memory ที่ไม่ได้ใช้ - สำคัญมากใน Long simulations
> - **Expression templates**: Compile-time optimization สำหรับ Field operations


**Best Practices:**
- ใช้ `tmp<T>` สำหรับ intermediate fields
- หลีกเลี่ยงการสร้าง field copies
- ใช้ `autoPtr<T>` สำหรับ large objects
- Reuse temporaries ใน loops
- Clear unused fields: `field.clear()`

### **Adaptive Mesh Refinement (AMR)**

**ประเภท Dynamic Mesh:**

| ประเภท | คำอธิบาย | การใช้งาน |
|--------|------------|-------------|
| **dynamicRefineFvMesh** | การ Refinement แบบ Cell-based ตาม Criteria | Localized phenomena |
| **dynamicFvMesh** | General dynamic mesh framework | Moving/deforming meshes |
| **dynamicMotionSolverFvMesh** | Motion solver coupled | Fluid-structure interaction |

**การตั้งค่า AMR:**

```cpp
// Adaptive mesh refinement configuration
// Dynamically refines mesh based on field gradients or other criteria
dynamicFvMesh   dynamicRefineFvMesh;

refinementLevel 2;  // Maximum refinement levels

refinementBoxes
{
    box1
    {
        min (0.1 0 0);
        max (0.2 1 1);
        cellSize 0.01;
    }
}

// Refinement criteria
refineInterval  1;  // Refine every time step

fields
(
    U
    p
);
```

> **📂 Source:** Standard OpenFOAM dynamic mesh configuration
>
> **คำอธิบาย:**
> - **dynamicRefineFvMesh**: แก้ Mesh แบบ Dynamic ตาม Criteria ที่กำหนด
> - **Refinement criteria**: เงื่อนไขที่ใช้ตัดสินใจ Refine/Derefine cells
> - **Max refinement levels**: จำกัดระดับการแบ่งเซลล์เพื่อป้องกัน Over-refinement
>
> **แนวคิดสำคัญ:**
> - **Adaptive refinement**: การปรับ Mesh ตาม Solution characteristics
> - **Gradient-based refinement**: การแบ่งเซลล์ที่มี Gradient สูง
> - **Load balancing**: การกระจาย Workload ใน Parallel AMR


**Refinement Criteria:**
$$\text{Refine if } |\nabla \phi| > \phi_{ref} \quad \text{and} \quad \Delta x > \Delta x_{min}$$

AMR มีคุณค่าสำหรับปัญหาที่มี Localized phenomena:
- **Shock waves**: Compressible flows
- **Flame fronts**: Combustion
- **Moving interfaces**: Multiphase flows
- **Boundary layers**: Near-wall refinement

> [!TIP] การใช้ AMR อย่างมีประสิทธิภาพ
> 1. เริ่มต้นด้วย coarse mesh
> 2. ตั้งค่า refinement criteria ที่เหมาะสม
> 3. จำกัด maximum refinement levels
> 4. ตรวจสอบ load balancing สำหรับ parallel runs

---

## การแก้ไขข้อผิดพลาดและการแก้ไขปัญหา (Debugging and Troubleshooting)

### **ปัญหาทั่วไปและการแก้ไข**

| ปัญหา | สาเหตุที่เป็นไปได้ | การแก้ไข | เครื่องมือวินิจฉัย |
|--------|------------------|-----------|-----------------|
| **Divergence** | Time step ใหญ่เกินไป, Mesh ไม่ดี | ลด Time step, ปรับ Under-relaxation | ตรวจสอบ residuals, Courant number |
| **Floating point exceptions** | Boundary conditions ไม่ถูกต้อง, Zero denominators | ตรวจสอบ BCs, เพิ่ม small value | `foamDebugSwitches`, Stack trace |
| **Matrix not factorizable** | Mesh quality แย่, Ill-conditioned matrix | ปรับปรุง Mesh, เปลี่ยน Solver | `checkMesh`, Condition number |
| **Slow convergence** | Bad initial guess, Inconsistent settings | ลด tolerances, ปรับ under-relaxation | Residual plotting |
| **Oscillations** | High order schemes, Large time steps | ลด order scheme, ลด time step | Time history monitoring |

### **เครื่องมือวินิจฉัย**

**1. checkMesh:**
```bash
# Full mesh quality check
checkMesh

# Specific geometry and topology checks
checkMesh -allGeometry -allTopology

# Write all field files for analysis
checkMesh -writeAllFields
```

**2. foamDebugSwitches:**
```bash
# Enable debug output for troubleshooting
foamDebugSwitches

# Check specific debug switches
foamDebugSwitches | grep -i solver

# Set global debug level
export FOAM_DEBUG=1
```

**3. Debug Functions:**
```cpp
// Monitoring and sampling functions for debugging
// Provides field data at specific locations and times
functions
{
    convergence
    {
        type            sets;
        libs            ("libfieldFunctionObjects.so");

        set             midLine;
        source          cellToPoint;
        fields
        (
            p
            U
        );
    }

    probes
    {
        type            probes;
        libs            ("libsampling.so");

        probeLocations  ( (0.1 0.1 0) (0.2 0.1 0) );
        fields          (p U k epsilon);
    }
}
```

> **📂 Source:** Standard OpenFOAM function objects
>
> **คำอธิบาย:**
> - **sets**: Sample fields ตาม Lines/planes ที่กำหนด
> - **probes**: Monitor fields ที่จุดเฉพาะ (Points) ตลอดเวลา
> - **Function objects**: Tools สำหรับ Monitoring และ Analysis ระหว่าง Simulation
>
> **แนวคิดสำคัญ:**
> - **Field sampling**: การเก็บข้อมูล Fields ที่ตำแหน่งที่สนใจ
> - **In-situ visualization**: การมองเห็นผลลัพธ์ระหว่าง Simulation
> - **Debugging output**: ข้อมูลเพิ่มเติมสำหรับ Diagnostics


**4. Performance Monitoring:**
```bash
# Get timing information from solver
mpirun -np 4 solver -parallel -parallel

# Profile code execution
foamProfiler

# List time directories to check storage
foamListTimes
```

### ขั้นตอนการแก้ปัญหาเชิงระบบ

```mermaid
graph TD
%% Troubleshooting Logic
Crash["Simulation Crash"]:::explicit

subgraph Diagnostics ["Diagnosis"]
Div["Divergence?"]:::context
BC["BC Error?"]:::context
Mesh["Bad Mesh?"]:::context
end

subgraph Actions ["Corrective Actions"]
Relax["Increase Under-Relaxation"]:::implicit
DT["Reduce Time Step"]:::implicit
Schemes["Use Upwind Schemes"]:::implicit
FixMesh["CheckNonOrtho / Refine"]:::implicit
end

Crash --> Diagnostics
Div --> Relax
Div --> DT
Div --> Schemes
Mesh --> FixMesh

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;
```
> **Figure 5:** ขั้นตอนการแก้ปัญหาอย่างเป็นระบบเมื่อการจำลองล้มเหลว โดยไล่เรียงจากการตรวจสอบประเภทของข้อผิดพลาด (เช่น การไม่ลู่เข้า หรือข้อผิดพลาดทางคณิตศาสตร์) ไปจนถึงการปรับปรุงพารามิเตอร์และการรันซ้ำ


### **Version Control ด้วย Git**

```bash
# Initialize git repository
git init

# Create .gitignore for OpenFOAM files
cat > .gitignore << EOF
# OpenFOAM outputs
*.bak
processor*
[0-9]*
[0-9]*.[0-9]*
*log.*
*log.*

# Core files
core
*.foam

# Editor files
*.swp
*~
.vscode/
.idea/
EOF

# Add and commit initial setup
git add .
git commit -m "Initial case setup"
```

> **📂 Source:** Standard version control practices for CFD
>
> **คำอธิบาย:**
> - **.gitignore**: ไฟล์ที่ระบุว่าไม่ต้อง Track ด้วย Git
> - **processor***: Subdomain files จาก Decomposition
> - **Time directories**: Directories ที่ชื่อเป็นตัวเลข (0, 0.1, 1, etc.)
>
> **แนวคิดสำคัญ:**
> - **Version control**: การติดตามการเปลี่ยนแปลงของ Source code และ Configuration
> - **Commit history**: บันทึกการแก้ไขทั้งหมด - สามารถย้อนกลับได้
> - **Collaboration**: การทำงานร่วมกันใน Team


### **กลยุทธ์การสำรองข้อมูล**

**1. Critical Time Snapshots:**
```bash
# Backup specific time directories
cp -r 5.0 5.0_backup
cp -r 10.0 10.0_backup
```

**2. Mesh and BC Files:**
```bash
# Separate mesh storage
mkdir -p MESH_BACKUP
cp -r constant/polyMesh MESH_BACKUP/
cp -r 0/* MESH_BACKUP/
```

**3. Automated Backup Scripts:**
```bash
#!/bin/bash
# Automated backup script for critical simulation data

CASE_DIR=$1
BACKUP_DIR=$2
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR/$TIMESTAMP

# Backup critical files
cp -r $CASE_DIR/constant/polyMesh $BACKUP_DIR/$TIMESTAMP/
cp -r $CASE_DIR/0 $BACKUP_DIR/$TIMESTAMP/
cp -r $CASE_DIR/system $BACKUP_DIR/$TIMESTAMP/

# Backup latest results
LATEST_TIME=$(ls -t $CASE_DIR | grep -E '^[0-9]+$' | head -1)
cp -r $CASE_DIR/$LATEST_TIME $BACKUP_DIR/$TIMESTAMP/

echo "Backup completed: $BACKUP_DIR/$TIMESTAMP"
```

> **📂 Source:** Standard backup strategies for CFD simulations
>
> **คำอธิบาย:**
> - **Critical files**: Mesh, BCs, System settings - สิ่งที่จำเป็นต้อง Backup
> - **Time snapshots**: Backup ที่จุดเวลาสำคัญ (เช่น หลังจาก Convergence)
> - **Automated scripts**: การ Backup อัตโนมัติเพื่อป้องกัน Data loss
>
> **แนวคิดสำคัญ:**
> - **Data integrity**: การรักษาความสมบูรณ์ของข้อมูล
> - **Recovery**: การกู้คืนข้อมูลหากเกิด Error หรือ Corruption
> - **Storage management**: การจัดการ Disk space สำหรับ Large simulations


### **เอกสารประกอบที่ควรรวม**

**README Template:**

```markdown
# Case Name

## Description
- Problem type: [e.g., Backward facing step]
- Fluid: [e.g., Water]
- Operating conditions: [e.g., Re = 10,000]

## Mesh
- Type: [e.g., Structured/Unstructured]
- Cell count: [e.g., 1M cells]
- Quality metrics:
  - Max non-orthogonality: [value]
  - Max skewness: [value]

## Solver Settings
- Solver: [e.g., simpleFoam]
- Schemes: [List key schemes]
- Tolerances: [List key tolerances]

## Boundary Conditions
- Inlet: [Description]
- Outlet: [Description]
- Walls: [Description]

## Running
- Decompose: `decomposePar`
- Run: `mpirun -np X solver -parallel`
- Reconstruct: `reconstructPar`

## Results
- Convergence: [Description]
- Key metrics: [e.g., Drag coefficient]

## Notes
- [Any special notes or issues]
```

> **📂 Source:** Standard documentation practices
>
> **คำอธิบาย:**
> - **README**: เอกสารที่อธิบาย Case และวิธีการ Run
> - **Reproducibility**: สามารถ Run ซ้ำได้โดยคนอื่น
> - **Documentation**: บันทึก Settings และ Results สำคัญ
>
> **แนวคิดสำคัญ:**
> - **Case metadata**: ข้อมูลเกี่ยวกับ Simulation problem
> - **Configuration tracking**: การบันทึก Settings ทั้งหมด
> - **Results documentation**: การบันทึก Key findings


---

## การเชื่อมโยง Multi-Physics (Multi-Physics Coupling)

### **กลยุทธ์การเชื่อมโยง**

**Sequential Coupling:**
- Physics ถูกแก้ตามลำดับ
- ง่ายกว่าแต่มีความแม่นยำน้อยกว่า
- Computational cost ต่ำ
- เหมาะสำหรับ Weakly coupled problems

**Coupled Solving:**
- สมการหลายสมการถูกแก้พร้อมกัน
- แม่นยำกว่าแต่มี Computational cost สูง
- เหมาะสำหรับ Strongly coupled problems
- ต้องการ Coupled solvers

```cpp
// Example of coupled solver for thermophysical problems
// Solves momentum and energy equations simultaneously
solve
(
    fvm::ddt(rho, U) + fvm::div(phi, U) - fvm::laplacian(mu, U)
 ==
    -grad(p)
);

solve
(
    fvm::ddt(rho, e) + fvm::div(phi, e) - fvm::laplacian(alpha, e)
 ==
    p*fvc::div(phi) + viscousHeating
);

p.ref() = rho*psi()*e.ref();  // Equation of state coupling
```

> **📂 Source:** Standard OpenFOAM coupled solver implementations
>
> **คำอธิบาย:**
> - **fvm::ddt**: Discretize time derivative แบบ Implicit
> - **fvm::div**: Discretize divergence term
> - **fvm::laplacian**: Discretize Laplacian operator
> - **Coupling**: การเชื่อมโยงระหว่าง Pressure, Density และ Energy
>
> **แนวคิดสำคัญ:**
> - **Multi-physics**: ปัญหาที่มี Physical phenomena หลายแบบ
> - **Two-way coupling**: Physics ต่างๆ มีผลต่อกันและกัน
> - **Convergence**: การลู่เข้าของ Coupled system ยากกว่า Single physics


### **การตรวจสอบความสอดคล้อง**

**1. Mass conservation:**
$$\sum_{\text{inlets}} \dot{m} - \sum_{\text{outlets}} \dot{m} = 0$$

**2. Energy balance:**
$$\dot{E}_{\text{in}} + \dot{Q}_{\text{generated}} = \dot{E}_{\text{out}} + \dot{Q}_{\text{stored}}$$

**3. Momentum conservation:**
$$\sum \mathbf{F}_{\text{pressure}} + \sum \mathbf{F}_{\text{viscous}} + \sum \mathbf{F}_{\text{body}} = 0 \quad \text{(steady-state)}$$

### **ข้อควรพิจารณาด้าน Stability**

1. **Time step selection**: ตาม Physics ที่เร็วที่สุด
   - Fluid time scale: $\Delta t_f \sim \frac{\Delta x}{|\mathbf{u}|}$
   - Thermal time scale: $\Delta t_T \sim \frac{\Delta x^2}{\alpha}$
   - Use minimum: $\Delta t = \min(\Delta t_f, \Delta t_T)$

2. **Boundary condition consistency**: สอดคล้องกันในทุก Physics
   - Temperature-dependent properties
   - Pressure-velocity coupling
   - Mass transfer coupling

3. **Scaling of coupled equations**:
   - Normalize variables
   - Balance equation magnitudes
   - Use appropriate preconditioning

---

## การตรวจสอบความถูกต้องและการยืนยัน (Validation and Verification)

### **Verification**

การยืนยัน Numerical implementation:

**Grid Convergence Study:**

```mermaid
graph LR
%% Grid Convergence
subgraph Meshes ["Mesh Levels"]
M1["Coarse"]:::implicit
M2["Medium"]:::implicit
M3["Fine"]:::implicit
end

subgraph Analysis ["Richardson Extrapolation"]
Result["Key Variable φ"]:::context
GCI["Grid Convergence Index"]:::explicit
Exact["Extrapolated Value"]:::implicit
end

M1 --> Result
M2 --> Result
M3 --> Result
Result --> GCI
GCI --> Exact

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;
```
> **Figure 6:** ขั้นตอนการศึกษาความอิสระของ Mesh (Grid convergence study) เพื่อการยืนยันผลเลขนัยสำคัญเชิงตัวเลข โดยการเปรียบเทียบผลลัพธ์จาก Mesh หลายขนาดเพื่อหาผลเฉลยที่แม่นยำที่สุด


1. สร้าง Mesh หลายขนาด (coarse, medium, fine)
2. ทำการจำลองบนแต่ละ Mesh
3. วิเคราะห์ Order of accuracy: $p = \frac{\ln|\phi_2 - \phi_1|}{\ln|\phi_3 - \phi_2|}$
4. ตรวจสอบ Richardson extrapolation: $\phi_{\infty} \approx \phi_3 + \frac{\phi_3 - \phi_2}{r^p - 1}$

**Time Step Independence:**
- ทำการจำลองด้วย Time steps หลายขนาด
- เปรียบเทียบ Solutions
- หา Time step ที่ Converged

```cpp
// Example time step study configuration
// Test temporal independence with different time steps
application     simpleFoam;

startFrom       startTime;
startTime       0;

stopAt          endTime;
endTime         1.0;

deltaT          0.001;  // Try: 0.001, 0.0005, 0.00025
```

> **📂 Source:** Standard OpenFOAM `controlDict` configuration
>
> **คำอธิบาย:**
> - **Grid convergence**: การตรวจสอบว่า Solution ไม่เปลี่ยนเมื่อ Mesh ละเอียดขึ้น
> - **Richardson extrapolation**: วิธีการประมาณ Solution ที่ mesh-independent
> - **Temporal independence**: การตรวจสอบว่า Solution ไม่เปลี่ยนเมื่อ Time step เล็กลง
>
> **แนวคิดสำคัญ:**
> - **Order of accuracy**: อัตราที่ Error ลดลงตาม Mesh refinement
> - **Asymptotic range**: ช่วงที่ Solution ลู่เข้าสู่ค่า grid-independent
> - **Uncertainty quantification**: การประเมิน Numerical uncertainty


### **Validation**

การเปรียบเทียบกับ Experimental หรือ Theoretical data:

**Benchmark Cases:**
- **Lid-driven cavity**: Classic benchmark
- **Backward facing step**: Separation and reattachment
- **Flow around cylinder**: Vortex shedding
- **Turbulent channel flow**: Wall-bounded turbulence

**Experimental Validation:**
- เปรียบเทียบกับการวัดจาก Wind tunnel
- Field measurements
- PIV (Particle Image Velocimetry) data
- Hot-wire anemometry

**Validation Metrics:**

| Metric | คำอธิบาย | การคำนวณ |
|--------|------------|-----------|
| **L₂ norm** | Root mean square error | $\sqrt{\frac{1}{N}\sum_{i=1}^{N}(\phi_{\text{CFD},i} - \phi_{\text{exp},i})^2}$ |
| **L∞ norm** | Maximum error | $\max_i |\phi_{\text{CFD},i} - \phi_{\text{exp},i}|$ |
| **Correlation coefficient** | Linear correlation | $\frac{\text{cov}(\phi_{\text{CFD}}, \phi_{\text{exp}})}{\sigma_{\text{CFD}} \sigma_{\text{exp}}}$ |
| **Relative error** | Percentage error | $\frac{|\phi_{\text{CFD}} - \phi_{\text{exp}}|}{|\phi_{\text{exp}}|} \times 100\%$ |

### **Uncertainty Quantification**

การประเมิน Sensitivity ต่อ Model parameters:

**1. Mesh sensitivity analysis:**
- Vary mesh density
- Monitor solution changes
- Establish mesh independence

**2. Time step sensitivity:**
- Vary time step size
- Check temporal accuracy
- Confirm Courant number criteria

**3. Turbulence model sensitivity:**
- Compare k-ε, k-ω, SST models
- Assess impact on key quantities
- Select appropriate model

**4. Boundary condition sensitivity:**
- Vary inlet profiles
- Test different outlet conditions
- Evaluate sensitivity to uncertainties

```cpp
// Sensitivity study example - convection schemes
// Compare different numerical schemes for the same problem

// Case 1: Central differencing
divSchemes { div(phi,U) Gauss linear; }

// Case 2: First-order upwind
divSchemes { div(phi,U) Gauss upwind; }

// Case 3: TVD scheme
divSchemes { div(phi,U) Gauss limitedLinear 1; }

// Compare results from all cases
```

> **📂 Source:** Standard OpenFOAM `fvSchemes` dictionary
>
> **คำอธิบาย:**
> - **Sensitivity analysis**: การวิเคราะห์ผลกระทบของ Parameter choices
> - **Numerical diffusion**: ข้อผิดพลาดจากการใช้ Scheme ลำดับต่ำ
> - **TVD schemes**: Total Variation Diminishing - สมดุลระหว่างความแม่นยำและเสถียรภาพ
>
> **แนวคิดสำคัญ:**
> - **Uncertainty**: ช่วงของค่าที่เป็นไปได้จาก Parameter variations
> - **Robustness**: ความทนทานของ Solution ต่อการเปลี่ยนแปลง
> - **Best practices**: การเลือก Settings ที่ให้ Results ที่น่าเชื่อถือ


---

## สรุป (Summary)

แนวปฏิบัติที่ดีที่สุดเหล่านี้ เมื่อนำไปใช้อย่างเป็นระบบ จะช่วยปรับปรุงความน่าเชื่อถือ ความแม่นยำ และประสิทธิภาพของการจำลอง OpenFOAM ในแอปพลิเคชัน CFD ที่หลากหลาย

### **Checklist ก่อนเริ่ม Simulation:**

- [ ] **Mesh Quality**: `checkMesh` passes all checks
- [ ] **Boundary Conditions**: Consistent and physically correct
- [ ] **Numerical Schemes**: Appropriate for flow physics
- [ ] **Solver Settings**: Tolerances and solvers configured
- [ ] **Initial Conditions**: Realistic starting field
- [ ] **Time Step**: CFL < 1 (explicit) or reasonable (implicit)
- [ ] **Parallel Setup**: Proper decomposition
- [ ] **Backup**: Mesh and initial conditions backed up
- [ ] **Documentation**: Case properly documented

### **Monitoring ระหว่าง Simulation:**

- [ ] **Residuals**: Decreasing appropriately
- [ ] **Courant Number**: Within acceptable limits
- [ ] **Mass Balance**: Conserved
- [ ] **Force Convergence**: Stable for steady-state
- [ ] **Field Monitors**: Physical behavior
- [ ] **Disk Space**: Sufficient available
- [ ] **Memory Usage**: Within limits

### **Post-Simulation Analysis:**

- [ ] **Convergence**: Properly converged
- [ ] **Conservation**: Mass, momentum, energy
- [ ] **Validation**: Compared with data/experiment
- [ ] **Verification**: Grid independence confirmed
- [ ] **Documentation**: Results properly archived
- [ ] **Backup**: Final results safely stored

> [!SUCCESS] การประยุกต์ใช้อย่างมืออาชีพ
> การปฏิบัติตามแนวทางเหล่านี้จะช่วยให้การจำลอง CFD ของคุณมีความน่าเชื่อถือ ผลลัพธ์ที่แม่นยำ และสามารถทำซ้ำได้ (reproducible) ซึ่งเป็นสิ่งสำคัญสำหรับงานวิจัยและการพัฒนาในอุตสาหกรรม