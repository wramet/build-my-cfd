# การประกอบเมทริกซ์ (Matrix Assembly)

## ภาพรวม

การประกอบเมทริกซ์ (Matrix Assembly) คือ **กระบวนการแปลงสมการอนุพันธ์ย่อย** (partial differential equations) ให้เป็น **ระบบสมการเชิงเส้น** (system of linear equations) ที่สามารถแก้ไขได้ด้วยวิธีเชิงตัวเลข

ใน OpenFOAM กระบวนการนี้เป็น **หัวใจสำคัญ** ของการแก้ปัญหา CFD ทั้งหมด โดยเชื่อมโยงระหว่าง:
- **Spatial Discretization**: การแบ่งโดเมนเป็น Control Volumes
- **Temporal Discretization**: การก้าวเวลาในการจำลอง
- **Linear Solvers**: การแก้ระบบสมการขนาดใหญ่

> [!INFO] **ความสำคัญ**
> การประกอบเมทริกซ์ที่ถูกต้องเป็นรากฐานของการจำลอง CFD ที่แม่นยำและเสถียร ข้อผิดพลาดในขั้นตอนนี้จะนำไปสู่ผลลัพธ์ที่คลาดเคลื่อนหรือการลู่เข้าที่ล้มเหลว

---

## จากสมการสู่เมทริกซ์

### การแปลงสมการควบคุม

พิจารณาสมการ Scalar Transport ทั่วไป:

$$\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \mathbf{u} \phi) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi$$

**เทอมของสมการ:**
- $\frac{\partial (\rho \phi)}{\partial t}$: เทอมเชิงเวลา (temporal term)
- $\nabla \cdot (\rho \mathbf{u} \phi)$: เทอมการพา (convection term)
- $\nabla \cdot (\Gamma \nabla \phi)$: เทอมการแพร่ (diffusion term)
- $S_\phi$: เทอมแหล่งกำเนิด (source term)

### กระบวนการ Discretization

เมื่ออินทิเกรตเหนือ Control Volume $V_P$ และประยุกต์ใช้ **Gauss Divergence Theorem**:

$$\int_{V_P} \frac{\partial (\rho \phi)}{\partial t} \, \mathrm{d}V + \int_{\partial V_P} (\rho \mathbf{u} \phi) \cdot \mathbf{n} \, \mathrm{d}S = \int_{\partial V_P} (\Gamma \nabla \phi) \cdot \mathbf{n} \, \mathrm{d}S + \int_{V_P} S_\phi \, \mathrm{d}V$$

ซึ่งนำไปสู่รูปแบบ Discrete สำหรับแต่ละเซลล์ $P$:

$$a_P \phi_P + \sum_{N} a_N \phi_N = b_P \tag{1}$$

โดยที่:
- $a_P$: สัมประสิทธิ์แนวทแยง (diagonal coefficient) สำหรับเซลล์ $P$
- $a_N$: สัมประสิทธิ์เพื่อนบ้าน (off-diagonal coefficients) สำหรับเซลล์ $N$
- $b_P$: เวกเตอร์แหล่งกำเนิด (source vector)
- ผลรวม $\sum_N$ เกิดขึ้นเหนือเซลล์เพื่อนบ้านทั้งหมดของเซลล์ $P$

### ระบบสมการเชิงเส้น

เมื่อเขียนสมการ (1) สำหรับ *ทุก* เซลล์ใน Mesh เราจะได้ระบบสมการเชิงเส้นขนาดใหญ่:

$$[A][x] = [b]$$

**องค์ประกอบของระบบ:**

| องค์ประกอบ | สัญลักษณ์ | คำอธิบาย |
|-----------|--------|----------------|
| **Coefficient Matrix** | $[A]$ | Sparse matrix ที่ประกอบด้วยสัมประสิทธิ์ ($a_P, a_N$) |
| **Solution Vector** | $[x]$ | Vector of unknowns (เช่น pressure ที่ทุกเซลล์) |
| **Source Vector** | $[b]$ | Vector ที่ประกอบด้วยเทอม explicit และ boundary values |

OpenFOAM solvers เช่น **PCG** (Preconditioned Conjugate Gradient) และ **PBiCG** (Preconditioned Bi-Conjugate Gradient) จะแก้ระบบเมทริกซ์นี้ด้วยวิธีวนซ้ำ (iterative methods)

---

## กรอบการทำงาน Finite Volume Discretization

### แนวทาง Cell-Centered

OpenFOAM ใช้แผนการทำให้เป็นส่วนย่อยแบบ **Finite Volume** ที่เน้น **cell-centered** โดยที่ตัวแปรหลักทั้งหมด (velocity, pressure, temperature, ฯลฯ) จะถูกเก็บไว้ที่จุดศูนย์กลางทางเรขาคณิตของเซลล์คำนวณ

```mermaid
graph LR
    subgraph CellCenteredFiniteVolume
        P["Cell P<br/>Owner Cell"]
        N["Cell N<br/>Neighbor Cell"]
        f["Face f<br/>Boundary Interface"]
        C_P["Center Point P<br/>(x_P, y_P, z_P)"]
        C_N["Center Point N<br/>(x_N, y_N, z_N)"]
        C_f["Face Center f<br/>(x_f, y_f, z_f)"]
        Sf["Surface Vector S_f<br/>S_f = n_f × A_f"]
        V_P["Cell Volume V_P<br/>Control Volume"]
        nf["Normal Vector n_f<br/>Unit Normal"]
        Af["Face Area A_f<br/>Surface Area"]

        P -- "Owner" --> f
        N -- "Neighbor" --> f
        P -- "Center" --> C_P
        N -- "Center" --> C_N
        f -- "Center" --> C_f
        f -- "Area Vector" --> Sf
        f -- "Normal" --> nf
        f -- "Area" --> Af
        P -- "Volume" --> V_P
    end

    style P fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style N fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style f fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style C_P fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,color:#000;
    style C_N fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,color:#000;
    style C_f fill:#ffebee,stroke:#c62828,stroke-width:1px,color:#000;
    style Sf fill:#fce4ec,stroke:#ad1457,stroke-width:1px,color:#000;
    style V_P fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px,color:#000;
    style nf fill:#e0f2f1,stroke:#00796b,stroke-width:1px,color:#000;
    style Af fill:#e0f2f1,stroke:#00796b,stroke-width:1px,color:#000;

    classDef cell fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef face fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef point fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,color:#000;
    classDef vector fill:#fce4ec,stroke:#ad1457,stroke-width:1px,color:#000;
    classDef property fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px,color:#000;

    class P,N cell;
    class f face;
    class C_P,C_N,C_f point;
    class Sf,nf,Af vector;
    class V_P property;
```

### ข้อมูลทางเรขาคณิตที่จำเป็น

**ข้อมูลทางเรขาคณิตที่ใช้ในการประกอบเมทริกซ์:**
- **ปริมาตรเซลล์** ($V_P$): ใช้สำหรับ Volume Integrals
- **พื้นที่ Face** ($|\mathbf{S}_f|$): ใช้สำหรับ Surface Integrals
- **เวกเตอร์แนวฉากของ Face** ($\mathbf{n}_f$): กำหนดทิศทางของ Flux
- **เวกเตอร์พื้นที่ผิว** ($\mathbf{S}_f = \mathbf{n}_f A_f$): ชี้จาก Owner Cell ไปยัง Neighbor Cell

แต่ละ Face มีเวกเตอร์พื้นที่ผิว $\mathbf{S}_f$ ที่ชี้จาก Owner Cell ไปยัง Neighbor Cell ข้อมูลทางเรขาคณิตนี้ช่วยให้สามารถคำนวณ:
- **Gradients**: การไหลของปริมาณในช่วงทางเชิงพื้นที่
- **Divergence Operations**: การไหลเข้า/ออกของ Control Volume
- **Flux Terms**: การถ่ายโอนปริมาณข้าม Face

### การประยุกต์ใช้ Gauss Divergence Theorem

สำหรับการแปลง Volume Integrals เป็น Surface Integrals:

$$\int_V \nabla \cdot \mathbf{F} \, \mathrm{d}V = \int_{\partial V} \mathbf{F} \cdot \mathbf{n} \, \mathrm{d}S$$

ใน Finite Volume Method:
$$\int_V \nabla \cdot \mathbf{F} \, \mathrm{d}V = \sum_{f} \mathbf{F}_f \cdot \mathbf{S}_f$$

---

## กระบวนการสร้างเมทริกซ์โดยละเอียด

### ขั้นตอนการประกอบเมทริกซ์

กระบวนการสร้างระบบเมทริกซ์ใน OpenFOAM เกี่ยวข้องกับ:

1. **Discretization**: สมการควบคุมอย่างเป็นระบบโดยใช้วิธี Finite Volume Method
2. **การแปลง**: รูปแบบอินทิกรัลของสมการการขนส่งเป็นรูปแบบพีชคณิต
3. **การประมาณค่า**: อินทิกรัลพื้นผิวและปริมาตรอย่างระมัดระวัง
4. **การใช้**: Gauss divergence theorem เพื่อแปลง Volume Integrals เป็น Surface Integrals

### คลาส `fvMatrix` Template Class

ในทางปฏิบัติ การประกอบเมทริกซ์ใน OpenFOAM จะถูกจัดการผ่าน **`fvMatrix` template class** ซึ่งจัดการโครงสร้าง Sparse Matrix ได้อย่างมีประสิทธิภาพ

```mermaid
graph TD
    A["Volume Field<br/>(Cell Center)"] -->|Interpolation| B["Surface Field<br/>(Face Center)"]
    B -->|Flux Calculation| C["Cell Face Gradient<br/>Gauss Theorem"]
    C -->|Discretization| D["fvMatrix Structure<br/>Sparse Linear System"]

    D --> E["Diagonal Coefficients<br/>A_D"]
    D --> F["Off-Diagonal Coefficients<br/>A_O"]
    D --> G["Source Vector<br/>b"]

    E --> H["Linear Solver<br/>Ax = b"]
    F --> H
    G --> H

    I["Interpolation Schemes"] --> B
    I --> J["Linear"]
    I --> K["Upwind"]
    I --> L["QUICK"]
    I --> M["TVD"]

    N["Conservation<br/>Principle"] --> C
    O["Boundedness<br/>Constraints"] --> B

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class A,B,C,H process;
    class D,E,F,G storage;
    class I,J,K,L,M decision;
    class N,O terminator;
```

### อัลกอริทึมการประกอบเมทริกซ์

การสร้างเมทริกซ์จริงใน OpenFOAM เป็นไปตามอัลกอริทึมที่เป็นระบบ:

```cpp
for (label cell = 0; cell < nCells; cell++)
{
    // Initialize diagonal coefficient
    a_P = 0.0;

    // Loop through all faces of this cell
    forAll(mesh.cells()[cell], faceI)
    {
        label face = mesh.cells()[cell][faceI];

        if (face < nInternalFaces)
        {
            // Internal face - contributes to both diagonal and off-diagonal
            label neighbor = mesh.owner()[face] == cell ?
                           mesh.neighbour()[face] : mesh.owner()[face];

            // Calculate face flux and coefficients
            scalar faceCoeff = calculateFaceCoefficient(face, cell, neighbor);

            // Off-diagonal contribution
            a_f[face] = -faceCoeff;

            // Diagonal contribution
            a_P += faceCoeff;
        }
        else
        {
            // Boundary face - contributes only to diagonal and source term
            scalar boundaryCoeff = calculateBoundaryContribution(face, cell);
            a_P += boundaryCoeff;
            b_P += boundaryCoeff * boundaryValue[face];
        }
    }

    // Add source terms
    b_P += sourceTerm[cell] * mesh.V()[cell];

    // Store in matrix structure
    matrix.setDiagonal(cell, a_P);
    for (label faceI = 0; faceI < nFacesPerCell; faceI++)
    {
        if (isInternalFace[faceI])
        {
            matrix.setOffDiagonal(cell, neighborCell[faceI], a_f[faceI]);
        }
    }
    matrix.setSource(cell, b_P);
}
```

---

## ความเบาบางและการจัดเก็บเมทริกซ์ (Matrix Sparsity and Storage)

### คุณสมบัติความเบาบางของเมทริกซ์

Coefficient matrix `[A]` ใน OpenFOAM แสดงโครงสร้างที่เบาบางมาก (highly sparse structure) เนื่องจาก:

- **Local Connectivity**: แต่ละเซลล์เชื่อมโยงเฉพาะกับเซลล์เพื่อนบ้านโดยตรงเท่านั้น
- **Finite Volume Discretization**: สมการแต่ละเซลล์เกี่ยวข้องเฉพาะเซลล์นั้นและเพื่อนบ้านที่ใกล้ที่สุด

**คุณสมบัติความเบาบาง:**
- สำหรับ Mesh แบบ 3D Unstructured ทั่วไปที่มีเซลล์ Polyhedral
- จำนวน Non-zero Entries ต่อแถวโดยเฉลี่ยประมาณ **12-20**
- แสดงถึงเซลล์เพื่อนบ้านโดยตรงของแต่ละเซลล์

### รูปแบบการจัดเก็บเมทริกซ์

| รูปแบบการจัดเก็บ | คำอธิบาย | การใช้งาน |
|---|---|---|
| **Compressed Sparse Row (CSR)** | รูปแบบการจัดเก็บเริ่มต้นที่แถวถูกจัดเก็บต่อเนื่องกัน | ค่าเริ่มต้นทั่วไป |
| **Diagonal storage** | สำหรับอัลกอริทึม Solver ที่ต้องการการเข้าถึง Diagonal บ่อยครั้ง | การปรับปรุงประสิทธิภาพ |
| **Symmetric storage** | เมื่อ Discretization ส่งผลให้เกิด Symmetric Coefficient Matrices | ปัญหา Symmetric |

> **Prompt:** Technical 3D isometric schematic of sparse matrix pattern [A] showing non-zero coefficients. Primary: Diagonal dominance visualization as thick blue lines. Secondary: Off-diagonal elements as thin gray connections between neighboring nodes. Annotations: Single-letter labels (P, N) using LaTeX notation. Clear sans-serif font for coefficients. Ray-traced studio lighting on semi-transparent materials. Style: Engineering illustration, high-contrast, white background, 8k resolution.

### โครงสร้างเมทริกซ์แบบ Sparse

```mermaid
graph LR
    A["Cell P"] --> B["Cell N1"]
    A --> C["Cell N2"]
    A --> D["Cell N3"]
    A --> E["Cell N4"]
    F["Face 1"] --> A
    F --> B
    G["Face 2"] --> A
    G --> C
    H["Face 3"] --> A
    H --> D
    I["Face 4"] --> A
    I --> E
    J["a_P coefficient"] --> A
    K["a_N1 coefficient"] --> B
    L["a_N2 coefficient"] --> C
    M["a_N3 coefficient"] --> D
    N["a_N4 coefficient"] --> E
    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style B fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style C fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style D fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style E fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style F fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style G fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style H fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style I fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style J fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style K fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style L fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style M fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style N fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
```

---

## ตัวอย่างการคำนวณสัมประสิทธิ์ (Coefficient Calculation Examples)

### ตัวอย่างสัมประสิทธิ์เมทริกซ์

สำหรับการแพร่กระจายแบบบริสุทธิ์ ($\nabla^2 \phi = 0$):

$$a_N = -\frac{\Gamma A_f}{d_{PN}} \tag{2}$$

$$a_P = -\sum_N a_N \tag{3}$$

โดยที่:
- $\Gamma$: สัมประสิทธิ์การแพร่ (diffusion coefficient)
- $A_f$: พื้นที่ Face
- $d_{PN}$: ระยะห่างระหว่างจุดศูนย์กลางเซลล์ P และ N

### เทอมการแพร่ (Diffusion Terms)

สำหรับกระบวนการที่เน้นการแพร่ (diffusion-dominated processes):

$$a_f = \frac{\Gamma_f A_f}{\delta_f} \tag{4}$$

โดยที่:
- $\Gamma_f = \frac{2\Gamma_P \Gamma_N}{\Gamma_P + \Gamma_N}$ (Harmonic Mean)
- $A_f$ คือพื้นที่ Face
- $\delta_f$ คือระยะห่างระหว่างจุดศูนย์กลางเซลล์

### เทอมการพา (Convection Terms)

สำหรับปัญหา Convection-Diffusion ที่ใช้ Upwind Differencing:

$$a_f = \rho_f \mathbf{u}_f \cdot \mathbf{S}_f + \frac{\Gamma_f A_f}{\delta_f} \tag{5}$$

โดยที่เครื่องหมายของเทอม Convective ขึ้นอยู่กับ:
- ทิศทางการไหล
- Upwind Scheme ที่ใช้

> **Prompt:** Technical 3D isometric schematic of finite volume cell interface between Cell P and Cell N. Primary: Velocity vector (u) as blue arrows showing flow direction through the face. Secondary: Face normal vector (n) as red perpendicular arrows. Face area vector (S_f) shown as yellow arrows. Distance vector (δ_f) shown as gray dashed line between cell centers. Annotations: Single-letter labels using LaTeX notation. Clear sans-serif font. Ray-traced studio lighting on semi-transparent materials. Style: Engineering illustration, high-contrast, white background, 8k resolution.

---

## การนำ Boundary Condition ไปใช้

### การจัดการ Boundary Condition ในเมทริกซ์

Boundary Conditions จะปรับเปลี่ยนสัมประสิทธิ์เมทริกซ์และ Source Terms ผ่านกลไกต่างๆ:

| ประเภท Boundary Condition | วิธีการใช้งาน | ผลกระทบ |
|---|---|---|
| **Dirichlet (Fixed Value)** | วิธี Penalty ขนาดใหญ่ หรือการปรับเปลี่ยนโดยตรง | แก้ไข Diagonal และ Source |
| **Neumann (Gradient)** | Zero-gradient หรือ Specified Gradient | ปรับเฉพาะ Source Terms |
| **Mixed (Robin)** | การรวมกันของข้อจำกัดด้านค่าและ Gradient | แก้ไขทั้ง Diagonal และ Source |
| **Calculated** | คำนวณจากตัวแปรอื่น ๆ ระหว่างการวนซ้ำ | Dependent ตามตัวแปรอื่น |

### การนำไปใช้ใน OpenFOAM

**Dirichlet Boundary**:
$$\phi_f = \phi_b$$

Contribution: $A_{PP} \mathrel{+=} \Gamma_f \frac{|\mathbf{S}_f|}{|\mathbf{d}_{Pb}|}$

**Neumann Boundary**:
$$\phi_f = \phi_P + (\nabla \phi)_b \cdot \mathbf{d}_{Pb}$$

Contribution: $A_{PP} \mathrel{+=} -\Gamma_f \frac{|\mathbf{S}_f|}{|\mathbf{d}_{Pb}|}, \quad b_P \mathrel{+=} \Gamma_f (\nabla \phi)_b \cdot \mathbf{S}_f$

> [!TIP] **Automatic Boundary Handling**
> กรอบการทำงานของ Boundary Condition จะจัดการการปรับเปลี่ยนเมทริกซ์ที่เหมาะสมโดยอัตโนมัติ ในขณะที่ยังคงรักษาเสถียรภาพเชิงตัวเลขและคุณสมบัติการลู่เข้า (convergence properties)

---

## การเพิ่มประสิทธิภาพการประกอบเมทริกซ์ (Matrix Assembly Optimization)

### กลยุทธ์การเพิ่มประสิทธิภาพ

OpenFOAM ใช้กลยุทธ์การเพิ่มประสิทธิภาพหลายอย่างเพื่อให้การประกอบเมทริกซ์มีประสิทธิภาพสูงสุด:

| กลยุทธ์ | คำอธิบาย | ประโยชน์ |
|---|---|---|
| **Cache-friendly memory access** | การจัดลำดับ Loop เพื่อเพิ่มการใช้ Cache ให้สูงสุด | ลด Memory Latency |
| **Vectorized operations** | คำสั่ง SIMD สำหรับการคำนวณสัมประสิทธิ์ | เพิ่ม Parallel Processing |
| **Parallel assembly** | Domain Decomposition และการสร้างเมทริกซ์แบบ Thread-safe | รองรับ Multi-core |
| **Lazy evaluation** | การคำนวณสัมประสิทธิ์ Face ที่มีค่าใช้จ่ายสูงแบบ Deferred | ลดการคำนวณซ้ำ |
| **Matrix reuse** | การอัปเดตแบบ Incremental สำหรับ Steady-state หรือ Pseudo-transient | เพิ่มความเร็วใน Convergence |

### การเพิ่มประสิทธิภาพด้วยฮาร์ดแวร์

**SIMD (Single Instruction, Multiple Data)**:
- ใช้คำสั่ง SIMD เพื่อคำนวณสัมประสิทธิ์หลายค่าพร้อมกัน
- เพิ่มประสิทธิภาพการคำนวณสำหรับ Mesh ที่มีเซลล์จำนวนมาก

**OpenMP Parallelization**:
- แบ่งการประกอบเมทริกซ์เป็น Threads หลายตัว
- ใช้งานได้ดีกับ Multi-core Processors

---

## การรวม Solver (Solver Integration)

### ประเภทของ Solver

ระบบเมทริกซ์ที่ประกอบขึ้นจะถูกแก้โดยใช้วิธี Iterative ที่ใช้ประโยชน์จากโครงสร้างเมทริกซ์:

| ประเภท Solver | วิธีการ | ปัญหาที่เหมาะสม |
|---|---|---|
| **Krylov subspace methods** | PCG, PBiCG, GMRES | ปัญหาทั่วไป |
| **Multigrid methods** | GAMG สำหรับ Geometric Algebraic Multigrid | ปัญหาขนาดใหญ่ |
| **Preconditioning** | Diagonal, ILU, AMG, PETSc Preconditioners | การเร่ง Convergence |
| **Convergence acceleration** | Relaxation Techniques และ Residual Smoothing | ปัญหาที่ยากต่อการลู่เข้า |

### การเลือก Solver และ Preconditioner

การเลือก Solver ที่เหมาะสมขึ้นอยู่กับ:

1. **ลักษณะของปัญหา**:
   - Symmetric vs. Non-symmetric matrices
   - Positive Definite vs. Indefinite matrices

2. **คุณสมบัติของเมทริกซ์**:
   - Condition number
   - Sparsity pattern
   - Matrix size

3. **ทรัพยากรการคำนวณที่มีอยู่**:
   - หน่วยความจำที่มี
   - จำนวน CPU cores
   - GPU availability

### ขั้นตอนการแก้สมการ

```mermaid
graph LR
    A["Matrix Assembly<br/>Complete"] --> B["Select Solver"]
    B --> C["Initialize Solution"]
    C --> D["Iterative Solution Loop"]
    D --> E["Compute Residual"]
    E --> F{"Converged?"}
    F -- No --> D
    F -- Yes --> G["Return Solution"]

    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style B fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style C fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style D fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style E fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000;
    style F fill:#e0f2f1,stroke:#00796b,stroke-width:2px,color:#000;
    style G fill:#fce4ec,stroke:#ad1457,stroke-width:2px,color:#000;
```

---

## การนำไปใช้ใน OpenFOAM

### ตัวอย่างการใช้งาน `fvMatrix`

**สมการคณิตศาสตร์**:
$$\frac{\partial \rho \mathbf{U}}{\partial t} + \nabla \cdot (\phi \mathbf{U}) - \nabla \cdot (\mu \nabla \mathbf{U}) = -\nabla p$$

### OpenFOAM Code Implementation

```cpp
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)                    // อนุพันธ์เชิงเวลาแบบ Implicit
  + fvm::div(phi, U)                    // เทอมการพาแบบ Implicit
  - fvm::laplacian(mu, U)               // เทอมการแพร่แบบ Implicit
 ==
    -fvc::grad(p)                       // เทอมความดันแบบ Explicit
);

UEqn.relax();                          // Relaxation สำหรับความเสถียร
solve(UEqn == -fvc::grad(p));          // แก้ระบบสมการ
```

### คลาสการทำให้เป็นส่วนย่อยหลัก

**คลาส Discretization หลักใน OpenFOAM:**
- **`fvm::ddt()`**: Temporal Derivative Discretization (implicit)
- **`fvc::ddt()`**: Explicit Temporal Derivative Calculation
- **`fvm::div()`**: Implicit Divergence Term Discretization
- **`fvc::div()`**: Explicit Divergence Term Calculation
- **`fvm::laplacian()`**: Implicit Laplacian Term Discretization
- **`fvc::grad()`**: Explicit Gradient Calculation

### ตัวอย่างการสร้างสมการ Energy

```cpp
fvScalarMatrix TEqn
(
    rho*cp*fvm::ddt(T)           // Temporal derivative
  + rho*cp*fvm::div(phi, T)       // Convection term
  - fvm::laplacian(k, T)          // Diffusion term
 ==
    Q                              // Source term
);

TEqn.relax();                     // Under-relaxation
solve(TEqn);                      // Solve the system
```

### การจัดการ Source Term

```cpp
// Add source term
UEqn += SU;

// Apply under-relaxation
UEqn.relax();

// Semi-implicit source term
fvScalarMatrix TEqn
(
    rho*cp*fvm::ddt(T)
  + rho*cp*fvm::div(phi, T)
  - fvm::laplacian(k, T)
 ==
    Q_explicit                    // Explicit source
  + fvm::Sp(S_implicit, T)        // Semi-implicit source
);
```

---

## บทสรุป

**การประกอบเมทริกซ์ (Matrix Assembly)** เป็นกระบวนการที่เป็นหัวใจสำคัญของการจำลอง CFD ใน OpenFOAM ซึ่งเชื่อมโยงระหว่างทฤษฎี Finite Volume Method กับการนำไปใช้ในโค้ดจริง

**ประเด็นสำคัญ:**

1. **Discretization**: การแปลงสมการอนุพันธ์ย่อยให้เป็นรูปแบบพีชคณิต
2. **Matrix Structure**: โครงสร้าง Sparse Matrix ที่เกิดจาก Finite Volume Method
3. **Coefficient Calculation**: การคำนวณสัมประสิทธิ์จาก Geometric Information และ Physical Properties
4. **Boundary Conditions**: การนำ Boundary Condition ไปใช้ในระบบเมทริกซ์
5. **Solver Integration**: การแก้ระบบสมการเชิงเส้นที่เกิดขึ้น

**ข้อดีของกรอบการทำงาน OpenFOAM:**
- การจัดการ Automatic Matrix Assembly
- ความยืดหยุ่นในการเลือก Discretization Schemes
- ประสิทธิภาพสูงสำหรับ Sparse Linear Systems
- การรองรับ Parallel Processing

> [!WARNING] **ข้อควรระวัง**
> การประกอบเมทริกซ์ที่ไม่ถูกต้องอาจนำไปสู่:
> - การลู่เข้าที่ล้มเหลว
> - ผลลัพธ์ที่คลาดเคลื่อนทางกายภาพ
> - ความไม่เสถียรเชิงตัวเลข

การเข้าใจกระบวนการประกอบเมทริกซ์อย่างลึกซึ้งเป็นสิ่งสำคัญสำหรับการพัฒนา Solver ที่มีประสิทธิภาพและแม่นยำใน OpenFOAM
