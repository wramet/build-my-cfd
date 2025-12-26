# แบบฝึกหัดเสริมทักษะ

> [!TIP] **วัตถุประสงค์ของแบบฝึกหัด**
> แบบฝึกหัดเหล่านี้ออกแบบมาเพื่อ **เสริมทักษะและความเข้าใจ** ในการใช้งาน OpenFOAM ผ่านการทดลองปรับเปลี่ยนพารามิเตอร์ต่างๆ ซึ่งจะช่วยให้คุณเข้าใจผลกระทบของแต่ละพารามิเตอร์ที่มีต่อผลลัพธ์การจำลอง

---

## 🎯 แบบฝึกหัดที่ 1: การปรับเปลี่ยน Reynolds Number

**เป้าหมาย:** เปลี่ยน `nu` ใน `constant/transportProperties` เป็น `0.001` ($Re=100$) และสังเกตพฤติกรรมการเคลื่อนที่ของจุดศูนย์กลางกระแสวน

### การวิเคราะห์การตั้งค่าปัจจุบัน

ก่อนทำการเปลี่ยนแปลง มาวิเคราะห์ค่าที่ตั้งไว้ในปัจจุบันกันก่อน

| พารามิเตอร์ | ค่าปัจจุบัน | หน่วย |
|------------|-------------|--------|
| **ความหนืดจลนศาสตร์ ($\nu$)** | 0.01 | m²/s |
| **ความเร็วของฝา ($U_{\text{lid}}$)** | 1 | m/s |
| **ความยาวลักษณะเฉพาะ ($L$)** | 0.1 | m |
| **Reynolds Number ($Re$)** | 10 | - |

### การคำนวณ Reynolds Number

Reynolds Number คำนวณได้จากสมการ:

$$Re = \frac{U_{\text{lid}} L}{\nu} = \frac{1 \times 0.1}{0.01} = \boxed{10}$$

### การดำเนินการ

ในไฟล์ `constant/transportProperties` เปลี่ยนค่าความหนืดเป็น:

```cpp
transportModel  Newtonian;

nu              [0 2 -1 0 0 0 0] 0.001;  // Kinematic viscosity in m²/s
                                         // Lower value = higher Reynolds number
```

> **📂 Source:** `constant/transportProperties`
>
> **คำอธิบาย:**
> - **transportModel:** ระบุชนิดของโมเดลความหนืด (Newtonian สำหรับของไหลที่ความหนืดคงที่)
> - **nu:** ความหนืดจลนศาสตร์ (Kinematic Viscosity) หน่วย m²/s
> - **[0 2 -1 0 0 0 0]:** Dimension ของค่าความหนืด (L²T⁻¹)
> - **0.001:** ค่าความหนืดใหม่ที่ต้องการเปลี่ยน (จาก 0.01 เป็น 0.001)
>
> **แนวคิดสำคัญ:**
> - การลดค่าความหนืดจะทำให้ Reynolds Number เพิ่มขึ้น
> - Reynolds Number สูงแสดงถึงแรงเฉื่อยมีอิทธิพลเหนือกว่าแรงหนืด
> - จะทำให้เกิดกระแสวนรองในมุม cavity และจุดศูนย์กลางกระแสวนจะเคลื่อนที่

**Reynolds Number ใหม่:**

$$Re_{\text{new}} = \frac{U_{\text{lid}} L}{\nu_{\text{new}}} = \frac{1 \times 0.1}{0.001} = \boxed{100}$$

### พฤติกรรมทางกายภาพที่คาดการณ์

#### ที่ $Re = 10$ (ปัจจุบัน)

- กระแสวนหลักเดียวที่ชัดเจน
- จุดศูนย์กลางอยู่ใกล้กึ่งกลาง Cavity
- การไหลยังคงสมมาตรค่อนข้างดี

#### ที่ $Re = 100$ (หลังการเปลี่ยนแปลง)

1. **การเคลื่อนที่ของจุดศูนย์กลางกระแสวน** — เลื่อน **ลงและไปทางผนังด้านขวา**
2. **กระแสวนรอง** — ปรากฏขึ้นใน **มุมด้านล่าง** (โดยเฉพาะมุมล่างขวา)
3. **ชั้นขอบเขต (Boundary Layer)** — บางลง ทำให้ Gradient ของความเร็วชันขึ้น
4. **ความไม่สมมาตร** — การไหลจะไม่สมมาตรมากขึ้น

### คำอธิบายทางกายภาพ

Reynolds Number แสดงถึงอัตราส่วนของแรงเฉื่อยต่อแรงหนืด:

$$Re = \frac{\text{Inertial Forces}}{\text{Viscous Forces}} = \frac{\rho \mathbf{u} \cdot \nabla \mathbf{u}}{\mu \nabla^2 \mathbf{u}}$$

**การนิยามตัวแปร:**

| สัญลักษณ์ | ความหมาย | หน่วย |
|---------|----------|--------|
| $\rho$ | ความหนาแน่นของของไหล | kg/m³ |
| $\mathbf{u}$ | เวกเตอร์ความเร็วของของไหล | m/s |
| $\mu$ | ความหนืดของของไหล | Pa·s |
| $\nabla$ | ตัวดำเนินการเกรเดียนต์ | - |
| $\nabla^2$ | ตัวดำเนินการ Laplacian | - |

ค่า $Re$ ที่สูงขึ้นหมายถึงแรงเฉื่อยมีอิทธิพลเหนือกว่า ทำให้โมเมนตัมของไหลพากระแสวนไปได้ไกลขึ้น

```mermaid
flowchart LR
    subgraph FlowRegimes["Flow Regime Evolution"]
        direction LR
        A["Re = 10<br/>Single Primary Vortex"]:::implicit --> B["Re = 100<br/>Vortex Shift & Asymmetry"]:::explicit
        B --> C["Secondary Vortices<br/>Corner Formation"]:::explicit
        C --> D["Thin Boundary Layers<br/>High Gradients"]:::volatile
    end

    subgraph Physics["Physical Interpretation"]
        direction LR
        E["Re = Inertia / Viscous"]:::context
        F["High Re = Momentum Dominated"]:::context
        G["Complexity Increases with Re"]:::context
    end

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
```
> **Figure 1:** การเปลี่ยนผ่านจากระบอบการไหลที่ $Re = 10$ ไปสู่ $Re = 100$ แสดงให้เห็นการเคลื่อนที่ของจุดศูนย์กลางกระแสวนหลักและการก่อตัวของกระแสวนรองในมุมของ Cavity เมื่อแรงเฉื่อยเริ่มมีอิทธิพลเหนือกว่าแรงหนืด

> หลังจากเปลี่ยนค่า `nu` แล้ว ให้รันคำสั่ง `blockMesh` และ `icoFoam` ใหม่ เพื่อดูผลลัพธ์ที่เปลี่ยนแปลงไป

---

## 🎯 แบบฝึกหัดที่ 2: การปรับปรุงความละเอียดของ Mesh

**เป้าหมาย:** เปลี่ยน `system/blockMeshDict` เป็น `(40 40 1)` และตรวจสอบ Grid Independence

### การตั้งค่า Mesh ปัจจุบัน

ในไฟล์ `system/blockMeshDict`:

```cpp
hex (0 1 2 3 4 5 6 7) (20 20 1) simpleGrading (1 1 1);  // Define hexahedral block
                                                        // (cells_x cells_y cells_z)
                                                        // simpleGrading: uniform spacing
```

> **📂 Source:** `system/blockMeshDict`
>
> **คำอธิบาย:**
> - **hex (0 1 2 3 4 5 6 7):** ระบุ vertices 8 จุดที่กำหนดรูปทรง Hexahedral block
> - **(20 20 1):** จำนวนเซลล์ในแต่ละทิศทาง (x, y, z)
> - **simpleGrading (1 1 1):** การกระจายตัวของเซลล์ (1 = สม่ำเสมอ)
>
> **แนวคิดสำคัญ:**
> - การเพิ่มจำนวนเซลล์จะเพิ่มความละเอียดของ Mesh
> - เซลล์มากขึ้น = ความแม่นยำสูงขึ้น แต่เวลาคำนวณนานขึ้น
> - การเปลี่ยนจาก 20 เป็น 40 เพิ่มเซลล์ 4 เท่า

### การดำเนินการ

เปลี่ยนจำนวนเซลล์เป็น 40×40:

```cpp
hex (0 1 2 3 4 5 6 7) (40 40 1) simpleGrading (1 1 1);  // Increase mesh resolution
                                                        // 40×40 cells in x-y plane
                                                        // 1 cell in z-direction (2D case)
```

> **📂 Source:** `system/blockMeshDict`
>
> **คำอธิบาย:**
> - **(40 40 1):** เพิ่มความละเอียดเป็น 40×40 เซลล์
> - จำนวนเซลล์รวม: 40 × 40 × 1 = 1,600 เซลล์
> - ขนาดเซลล์: Δx = 0.1/40 = 0.0025 m
>
> **แนวคิดสำคัญ:**
> - Grid Independence คือการตรวจสอบว่าผลลัพธ์ไม่เปลี่ยนแปลงเมื่อเพิ่มความละเอียด Mesh
> - หากค่าต่างกันน้อยกว่า 2% ถือว่าได้รับ Grid Independence
> - Mesh ละเอียดขึ้นจะแสดงรายละเอียดของกระแสวนรองได้ดีขึ้น

### การเปรียบเทียบ Mesh

| คุณสมบัติ | Mesh หยาบ (20×20) | Mesh ละเอียด (40×40) |
|------------|-------------------|---------------------|
| **จำนวนเซลล์** | 400 เซลล์ | 1,600 เซลล์ (เพิ่ม 4×) |
| **ขนาดเซลล์ ($\Delta x$)** | 0.005 m | 0.0025 m |
| **ข้อผิดพลาด ($O(\Delta x^2)$)** | $\approx 2.5 \times 10^{-5}$ | $\approx 6.25 \times 10^{-6}$ |

### การเปลี่ยนแปลงที่คาดการณ์

1. **ตำแหน่งจุดศูนย์กลางกระแสวน** — แม่นยำขึ้น **1-3%**
2. **ขนาดความเร็ว** — ความเร็วสูงสุดอาจเพิ่มขึ้น **2-5%**
3. **กระแสวนรอง** — แสดงโครงสร้างขนาดเล็กในมุมต่างๆ ได้ดีขึ้น
4. **การลู่เข้า** — Residuals ลู่เข้าดีขึ้น

### เกณฑ์ Grid Independence

คำตอบถือว่าเป็น **Grid-independent** เมื่อ:

$$\frac{|\phi_{\text{fine}} - \phi_{\text{coarse}}|}{|\phi_{\text{fine}}|} < 0.02$$

**การนิยามตัวแปร:**

| สัญลักษณ์ | ความหมาย |
|---------|----------|
| $\phi_{\text{fine}}$ | ค่าจาก Mesh ละเอียด |
| $\phi_{\text{coarse}}$ | ค่าจาก Mesh หยาบ |
| $\phi$ | ปริมาณที่สนใจ (ตำแหน่งจุดศูนย์กลางกระแสวน, ความเร็วสูงสุด) |

```mermaid
flowchart LR
    A["Mesh Configuration"]:::context --> B["Coarse Mesh<br/>(20×20)"]:::implicit
    A --> C["Fine Mesh<br/>(40×40)"]:::implicit
    
    B --> B1["Δx = 0.005 m"]:::context
    B --> B2["Higher Error"]:::volatile
    
    C --> C1["Δx = 0.0025 m"]:::context
    C --> C2["Lower Error"]:::success
    
    B2 --> D["Grid Independence Check"]:::explicit
    C2 --> D
    
    D --> E["Error Metric<br/>< 2% Difference"]:::explicit
    D --> F["Comparison Metrics"]:::explicit
    
    F --> F1["Vortex Center<br/>+1-3%"]:::context
    F --> F2["Max Velocity<br/>+2-5%"]:::context
    F --> F3["Resolution Improved"]:::success
    F --> F4["Convergence Improved"]:::success

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
```
> **Figure 2:** การเปรียบเทียบระหว่าง Mesh แบบหยาบ (20×20) แับ Mesh แบบละเอียด (40×40) เพื่อใช้ในการตรวจสอบ Grid Independence โดยวิเคราะห์ความแม่นยำของตำแหน่งกระแสวนและความเร็วสูงสุดที่เพิ่มขึ้นเมื่อลดขนาดของเซลล์ลง

> Mesh ที่ละเอียดขึ้นจะใช้เวลาในการคำนวณนานขึ้น ให้พิจารณา Balance ระหว่างความแม่นยำและเวลาในการคำนวณ

---

## 🎯 แบบฝึกหัดที่ 3: การใช้ Solver แบบ Steady-State

**เป้าหมาย:** รัน `simpleFoam` แทน `icoFoam` และปรับ `system/controlDict` และ `system/fvSolution`

### ความแตกต่างของ Solver

| คุณสมบัติ | icoFoam (Transient) | simpleFoam (Steady-state) |
|------------|---------------------|---------------------------|
| **อัลกอริทึม** | PISO | SIMPLE |
| **สมการโมเมนตัม** | $\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu \nabla^2 \mathbf{u}$ | $(\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu \nabla^2 \mathbf{u}$ |
| **การหาคำตอบ** | Time marching | Iterative solution |

### การปรับ `system/controlDict`

```cpp
// For simpleFoam (steady-state)
application     simpleFoam;           // Use steady-state solver
startFrom       startTime;            // Start from latestTime
startTime       0;                    // Initial time value
stopAt          endTime;              // Stop when endTime is reached
endTime         1000;                 // Pseudo-time steps for convergence
deltaT          1;                    // Time step size (not physical time)
adjustTimeStep  no;                   // Fixed time step
```

> **📂 Source:** `system/controlDict`
>
> **คำอธิบาย:**
> - **simpleFoam:** Solver สำหรับ steady-state, incompressible, turbulent flow
> - **endTime 1000:** จำนวน iterations สูงสุดสำหรับการลู่เข้า
> - **deltaT 1:** ใน steady-state ไม่มีความหมายทางกายภาพของเวลา ใช้เป็น iteration counter
>
> **แนวคิดสำคัญ:**
> - SIMPLE ใช้ under-relaxation เพื่อความเสถียรของการวนซ้ำ
> - ไม่ต้องการ temporal discretization เพราะหาคำตอบ steady-state
> - การลู่เข้าถูกตรวจสอบด้วย residuals ไม่ใช่เวลา

### การปรับ `system/fvSolution`

```cpp
solvers
{
    p
    {
        solver          GAMG;              // Geometric-Algebraic Multi-Grid solver
        tolerance       1e-06;             // Absolute tolerance convergence
        relTol          0.1;               // Relative tolerance (10% of initial residual)
        smoother        GaussSeidel;       // Smoother for GAMG
        nCellsInCoarsestLevel 10;          // Minimum cells in coarsest grid level
    }

    U
    {
        solver          smoothSolver;      // Iterative solver for velocity
        smoother        GaussSeidel;       // Smoother type
        tolerance       1e-05;             // Absolute tolerance
        relTol          0;                 // Tight convergence (0% relative tolerance)
    }
}

SIMPLE
{
    nCorrectors      2;                   // Number of pressure correction loops
    nNonOrthogonalCorrectors 0;           // Non-orthogonal correction loops
    pRefCell        0;                    // Reference cell for pressure
    pRefValue       0;                    // Reference pressure value (Pa)
    residualControl
    {
        p               1e-5;             // Convergence criterion for pressure
        U               1e-5;             // Convergence criterion for velocity
    }
}

relaxationFactors
{
    fields
    {
        p               0.3;               // Pressure under-relaxation factor
    }
    equations
    {
        U               0.7;               // Momentum under-relaxation factor
    }
}
```

> **📂 Source:** `.applications/test/patchRegion/cavity_pinched/system/fvSolution`
>
> **คำอธิบาย:**
> - **GAMG:** Generalized Geometric-Algebraic Multi-Grid solver สำหรับ pressure
> - **smoothSolver:** Solver แบบ iterative สำหรับ velocity
> - **SIMPLE:** Semi-Implicit Method for Pressure-Linked Equations algorithm
> - **nCorrectors:** จำนวนรอบการแก้ไข pressure ในแต่ละ iteration
> - **relaxationFactors:** ค่า under-relaxation สำหรับความเสถียร
>
> **แนวคิดสำคัญ:**
> - Under-relaxation จำเป็นสำหรับ steady-state เพื่อป้องกันการ oscillate
> - Pressure relaxation (0.3) ต่ำกว่า velocity (0.7) เพราะ pressure ไวต่อการเปลี่ยนแปลงมากกว่า
> - residualControl ใช้ตรวจสอบว่า solution ลู่เข้าแล้ว

### ความแตกต่างสำคัญสำหรับ Steady-State

1. **Under-Relaxation** — จำเป็นสำหรับการลู่เข้า ช่วยป้องกันการสั่นของผลเฉลย
2. **Residual Monitoring** — ตรวจสอบว่า Residuals ลดลงต่ำกว่า Tolerance
3. **ไม่มี Time Marching** — ใช้ Pseudo-time stepping เพื่อความเสถียร
4. **Pressure Solver** — GAMG เป็นที่นิยมสำหรับปัญหา Steady-state

---

## 📊 การตรวจสอบคุณภาพการจำลอง

### การตรวจสอบการลู่เข้า (Convergence Monitoring)

#### สำหรับ transient solver (icoFoam)

- ตรวจสอบ Residuals ต่อเวลา
- ตรวจสอบความสมบูรณ์ของมวล: $\nabla \cdot \mathbf{u} = 0$

#### สำหรับ steady-state solver (simpleFoam)

```bash
foamJob simpleFoam -case cavity
```

### การตรวจสอบแรง (Force Monitoring)

เพิ่ม `functions` ใน `system/controlDict`:

```cpp
functions
{
    forces
    {
        type            forces;            // Function object type for force calculation
        functionObjectLibs ("libforces.so");  // Library containing forces function
        outputControl   timeStep;          // Output frequency control
        outputInterval  1;                 // Output every time step
        log             true;              // Write to log file
        patches         ("movingWall");    // Patches to calculate forces on
        rho             rhoInf;            // Density type
        rhoInf          1;                 // Reference density (kg/m³)
    }
}
```

> **📂 Source:** `system/controlDict`
>
> **คำอธิบาย:**
> - **forces:** Function object สำหรับคำนวณแรงและโมเมนต์ที่ผนัง
> - **libforces.so:** Library ที่มี force calculation functions
> - **movingWall:** Patch ที่ต้องการคำนวณแรง
> - **rhoInf 1:** ความหนาแน่นของของไหลสำหรับ incompressible flow
>
> **แนวคิดสำคัญ:**
> - การตรวจสอบแรงช่วย validate ว่าการจำลองถูกต้อง
> - สามารถเปรียบเทียบกับข้อมูล benchmark ได้
> - Drag และ Lift forces สำคัญสำหรับปัญหาพื้นฐาน

### กลยุทธ์การตรวจสอบความถูกต้อง (Validation Strategy)

#### การเปรียบเทียบกับข้อมูลอ้างอิง

- **Ghia et al. (1982)** — ข้อมูลมาตรฐานสำหรับ Lid-driven cavity
- **Benchmark Solutions** — ตำแหน่งจุดศูนย์กลางกระแสวนและความเร็วสูงสุด

#### การตรวจสอบความสมบูรณ์

| ประเภท | เงื่อนไข |
|--------|-----------|
| **Mass Conservation** | $\nabla \cdot \mathbf{u} = 0$ |
| **Momentum Balance** | การสมดุลของแรงที่ผนัง |
| **Grid Independence** | การลู่เข้าของคำตอบเมื่อละเอียด Mesh |

---

## 🎯 บทสรุปแบบฝึกหัด

### ผลลัพธ์การเรียนรู้

1. **ผลกระทบของ Reynolds Number** — เข้าใจว่าการเปลี่ยนค่า $Re$ ส่งผลต่อรูปร่างกระแสวนอย่างไร
2. **Grid Independence** — เรียนรู้วิธีการตรวจสอบว่า Mesh มีความละเอียดเพียงพอ
3. **อัลกอริทึม Solver** — เปรียบเทียบ PISO และ SIMPLE และเข้าใจว่าเมื่อไหร่ควรใช้อัลกอริทึมใด

### ทักษะที่ได้รับ

| ทักษะ | คำอธิบาย |
|-------|----------|
| **การกำหนดค่า OpenFOAM** | สามารถปรับพารามิเตอร์ต่างๆ ได้อย่างถูกต้อง |
| **การวิเคราะห์ผลลัพธ์ CFD** | เข้าใจผลลัพธ์ที่ได้จากการจำลอง |
| **การตรวจสอบความถูกต้อง** | สามารถตรวจสอบความถูกต้องของผลลัพธ์ได้ |
| **การปรับปรุงความละเอียด Mesh** | สามารถสร้าง Mesh ที่เหมาะสมกับปัญหาได้ |

---

**🎉 การจำลอง OpenFOAM ครั้งแรกของคุณเสร็จสมบูรณ์!**

คุณได้ตั้งค่า Mesh, Boundary Conditions และ Physics ได้สำเร็จ และได้แก้สมการ Navier-Stokes แล้ว การทำแบบฝึกหัดเหล่านี้จะช่วยให้คุณเข้าใจการทำงานของ OpenFOAM ได้อย่างลึกซึ้งยิ่งขึ้น