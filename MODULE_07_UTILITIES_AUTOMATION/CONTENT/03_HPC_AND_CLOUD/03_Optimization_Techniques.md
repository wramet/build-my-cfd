# 🔧 เทคนิคการเพิ่มประสิทธิภาพขั้นสูง (Optimization Techniques)

> [!INFO] **ภาพรวมของการปรับปรุงประสิทธิภาพ**
> บทนี้ครอบคลุมเทคนิคขั้นสูงในการเพิ่มประสิทธิภาพการจำลองแบบขนาน (Parallel Simulation) ของ OpenFOAM รวมถึงการตั้งค่า Solver, การจัดการหน่วยความจำ, การเพิ่มประสิทธิภาพ I/O, การปรับแต่ง Algorithmic, และการวิเคราะห์ประสิทธิภาพสำหรับการแก้ปัญหาขนาดใหญ่

---

## 1. การปรับแต่ง Solver (Solver Tuning)

การเลือกพารามิเตอร์ของ Solver อย่างเหมาะสมสามารถลดเวลาการคำนวณลงได้มหาศาลโดยไม่เสียความแม่นยำ

### 1.1 การตั้งค่า fvSolution

#### 1.1.1 Pressure Solver Configuration

สำหรับปัญหาที่มีความดันเป็นตัวแปรสำคัญ (Pressure-driven flows), การเลือก Pressure Solver ที่เหมาะสมมีความสำคัญอย่างยิ่ง สมการความดัน Poisson ที่แก้ด้วย GAMG solver:

$$ \nabla \cdot \left( \frac{1}{A_p} \nabla p \right) = \frac{\partial}{\partial t} \left( \nabla \cdot \mathbf{U} \right) $$

โดยที่:
- $p$ คือ ความดัน (Pressure)
- $A_p$ คือ สัมประสิทธิ์เมทริกซ์ของเซลล์กลาง (Central coefficient)
- $\mathbf{U}$ คือ เวกเตอร์ความเร็ว (Velocity vector)

```cpp
// NOTE: Synthesized by AI - Verify parameters
// Optimized fvSolution settings for incompressible flow
solvers
{
    p
    {
        solver          GAMG;  // Recommended for pressure (Multigrid)
        tolerance       1e-06;
        relTol          0.01;
        smoother        GaussSeidel;
        cacheAgglomeration on;
        agglomerator    faceAreaPair;
        nCellsInCoarsestLevel 10;
        nPreSweeps      0;
        nPostSweeps     2;
        nFinestSweeps   2;
        mergeLevels     1;
    }

    pFinal
    {
        $p;
        relTol          0;
    }

    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
        nSweeps         1;
    }

    "(k|epsilon|omega|nuTilda)"
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}
```

> 📂 **Source:** `.applications/utilities/parallelProcessing/decomposePar/decomposePar.C`

> **คำอธิบาย (Thai Explanation):**
> การตั้งค่า Solver ใน `fvSolution` สำหรับการไหลแบบอัดตัวไม่ได้ (Incompressible Flow) โดยเน้นการเพิ่มประสิทธิภาพดังนี้:
> - **GAMG (Geometric-Algebraic Multi-Grid)**: Solver สำหรับความดันที่ใช้เทคนิค Multigrid ซึ่งมีประสิทธิภาพสูงสำหรับระบบขนาน
> - **cacheAgglomeration**: เก็บข้อมูลการรวมเซลล์ไว้ใน cache เพื่อเร่งความเร็ว
> - **nCellsInCoarsestLevel**: จำนวนเซลล์ในระดับหยาบที่สุดของ Multigrid (ค่าน้อย = ระดับมากขึ้น = ลู่เข้าเร็วขึ้นแต่ใช้หน่วยความจำมากขึ้น)
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Multigrid Acceleration**: GAMG ใช้การแก้สมการในหลายระดับความละเอียด เพื่อลดความถี่ของ Error modes
> 2. **Sweeps**: รอบการคำนวณในแต่ละระดับ - nPreSweeps ก่อนลงระดับ, nPostSweeps หลังขึ้นระดับ
> 3. **pFinal**: การตั้งค่าพิเศษสำหรับ iteration สุดท้ายโดยใช้ relTol = 0 (converge สุด)

> [!TIP] **GAMG Solver Performance**
> อัลกอริทึม Geometric-Algebraic Multi-Grid (GAMG) มีประสิทธิภาพสูงมากสำหรับการแก้สมการความดันในระบบขนาน เนื่องจากช่วยลดจำนวนรอบการวนซ้ำ (Iterations) ลงได้มาก โดยเฉพาะสำหรับ Mesh ที่มีจำนวนเซลล์มากกว่า 1 ล้านเซลล์ ความซับซ้อนของการคำนวณของ GAMG คือ $O(N \log N)$ เมื่อเทียบกับ $O(N^2)$ สำหรับ iterative solvers แบบดั้งเดิม

#### 1.1.2 Compressible Flow Solvers

สำหรับการไหลแบบบีบอัดได้ (Compressible flows) ต้องการการตั้งค่าที่แตกต่างออกไป:

```cpp
// NOTE: Synthesized by AI - Verify parameters
// Solver settings for compressible flows (rhoPimpleFoam, rhoSimpleFoam)
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-07;
        relTol          0.01;
        smoother        GaussSeidel;
        cacheAgglomeration on;
        nCellsInCoarsestLevel 20;
    }

    rho
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }

    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;  // Symmetric for better convergence
        tolerance       1e-06;
        relTol          0.1;
        nSweeps         2;
    }

    h  // Enthalpy for compressible flows
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-06;
        relTol          0.1;
    }

    "(k|epsilon|omega)"
    {
        $U;
    }
}
```

> 📂 **Source:** `.applications/solvers/compressible/rhoSimpleFoam/rhoSimpleFoam.C`

> **คำอธิบาย (Thai Explanation):**
> การตั้งค่า Solver สำหรับการไหลแบบอัดตัวได้ (Compressible Flow) มีความแตกต่างจาก Incompressible ดังนี้:
> - **symGaussSeidel**: Symmetric Gauss-Seidel smoother สำหรับการลู่เข้าที่ดีกว่าในระบบ compressible
> - **rho**: Solver สำหรับความหนาแน่น ซึ่งมีความสำคัญมากใน compressible flow
> - **h (Enthalpy)**: การแก้สมการเอนทาลปีซึ่งจำเป็นสำหรับ compressible flow
> - **nSweeps = 2**: จำนวนรอบการวนซ้ำที่มากขึ้นสำหรับ stability ที่ดีขึ้น
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Coupled System**: ใน compressible flow, pressure, density และ enthalpy เชื่อมโยงกันอย่างใกล้ชิด
> 2. **Tighter Tolerance**: pressure tolerance ที่ 1e-07 เพื่อความแม่นยำในการคำนวณความหนาแน่น
> 3. **Smoother Selection**: symGaussSeidel ให้ convergence ที่ดีกว่าสำหรับ non-symmetric systems

#### 1.1.3 Algorithm Settings

```cpp
// NOTE: Synthesized by AI - Verify parameters
// Algorithm settings in fvSolution
algorithms
{
    p
    {
        solver          GAMG;
        tolerance       1e-7;
        relTol          0.01;
    }
}

// Settings for PIMPLE algorithm (transient)
PIMPLE
{
    nCorrectors      2;        // Number of pressure correctors
    nNonOrthogonalCorrectors 0;  // For non-orthogonal mesh
    nAlphaCorr      1;        // For VOF (interFoam)
    nAlphaSubCycles 2;        // Sub-cycles for volume fraction

    momentumPredictor yes;     // Predict momentum before pressure equation

    // Tuning relaxation factors
    nOuterCorrectors  50;      // Maximum iterations per time step
    relTol           0.01;     // Relative tolerance for outer loop
}
```

> 📂 **Source:** `.applications/solvers/incompressible/pimpleFoam/PIMPLE.C`

> **คำอธิบาย (Thai Explanation):**
> การตั้งค่า PIMPLE Algorithm ซึ่งเป็นการรวมกันของ PISO (Pressure Implicit with Splitting of Operators) และ SIMPLE (Semi-Implicit Method for Pressure-Linked Equations):
> - **nCorrectors**: จำนวนรอบการแก้ไข pressure ในแต่ละ time step (PISO part)
> - **nOuterCorrectors**: จำนวนรอบภายนอกสูงสุด (SIMPLE part) สำหรับ transient simulations
> - **momentumPredictor**: ทำนายความเร็วก่อนแก้สมการ pressure เพื่อเพิ่มความเสถียร
> - **nAlphaCorr**: จำนวนรอบการแก้ไข volume fraction สำหรับ VOF methods
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **PIMPLE Hybrid**: ผสมผสาน PISO (transient, 2-3 corrections) กับ SIMPLE (steady-state, multiple outer iterations)
> 2. **Outer Loop**: วนซ้ำจนกว่าจะ converge หรือถึง nOuterCorrectors
> 3. **Sub-cycling**: ใช้ time steps ย่อยสำหรับ terms ที่มีความเร็วสูง (เช่น VOF)

### 1.2 การปรับสมดุล Tolerance

การตั้งค่า Tolerance ที่เหมาะสมเป็นการแลกเปลี่ยนระหว่างความแม่นยำและเวลาในการคำนวณ:

$$ \text{Convergence Criteria: } \frac{||\mathbf{r}^{(k)}||}{||\mathbf{r}^{(0)}||} \leq \epsilon_{\text{rel}} \quad \text{หรือ} \quad ||\mathbf{r}^{(k)}|| \leq \epsilon_{\text{abs}} $$

โดยที่:
- $\mathbf{r}^{(k)}$ คือ Residual ที่ iteration ที่ $k$
- $\epsilon_{\text{rel}}$ คือ Relative tolerance (`relTol`)
- $\epsilon_{\text{abs}}$ คือ Absolute tolerance (`tolerance`)
- $||\cdot||$ คือ L2-norm

สำหรับระบบขนาน Residual ถูกคำนวณเป็น global norm:

$$ ||\mathbf{r}|| = \sqrt{\sum_{i=1}^{N} r_i^2} = \sqrt{\sum_{p=1}^{P} \sum_{j \in \Omega_p} r_j^2} $$

โดยที่:
- $N$ คือ จำนวนเซลล์ทั้งหมด
- $P$ คือ จำนวน processors
- $\Omega_p$ คือ เซตของเซลล์ใน processor $p$

> [!WARNING] **คำเตือนเรื่อง Tolerance**
> การตั้งค่า `relTol` สูงเกินไป (เช่น 0.5 ขึ้นไป) อาจทำให้การคำนวณไม่ลู่เข้า (Non-converged solution) ในทางกลับกัน การตั้งค่าต่ำเกินไป (เช่น 1e-8) อาจทำให้เสียเวลาในการคำนวณโดยไม่จำเป็น คำแนะนำ: `relTol = 0.01` สำหรับ intermediate iterations และ `relTol = 0` สำหรับ final iterations

### 1.3 Preconditioning Techniques

Preconditioning ช่วยปรับปรุงอัตราการลู่เข้าของ solvers:

$$ \mathbf{M}^{-1} \mathbf{A} \mathbf{x} = \mathbf{M}^{-1} \mathbf{b} $$

โดยที่ $\mathbf{M}$ คือ preconditioner matrix

```cpp
// NOTE: Synthesized by AI - Verify parameters
// Preconditioning for difficult cases
solvers
{
    p
    {
        solver          GAMG;
        preconditioner  DIC;     // Diagonal Incomplete Cholesky
        tolerance       1e-06;
        relTol          0.01;
    }

    U
    {
        solver          PBiCGStab;  // For non-symmetric systems
        preconditioner  DILU;       // Diagonal Incomplete LU
        tolerance       1e-05;
        relTol          0.1;
        minIter         0;
        maxIter         1000;
    }
}
```

> 📂 **Source:** `.src/OpenFOAM/matrices/solvers/Preconditioners`

> **คำอธิบาย (Thai Explanation):**
> การใช้ Preconditioning เพื่อเร่งอัตราการลู่เข้าของ iterative solvers:
> - **DIC (Diagonal Incomplete Cholesky)**: Preconditioner สำหรับ symmetric positive definite matrices (เช่น pressure equation)
> - **DILU (Diagonal Incomplete LU)**: Preconditioner สำหรับ non-symmetric matrices (เช่น momentum equation)
> - **PBiCGStab**: Stabilized Bi-Conjugate Gradient solver สำหรับ systems ที่ไม่สมมาตร
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Preconditioning Matrix**: $\mathbf{M}$ เป็น approximation ของ $\mathbf{A}$ ที่ง่ายต่อการ invert
> 2. **Incomplete Factorization**: LU/Cholesky แบบไม่สมบูรณ์เพื่อประหยัดหน่วยความจำ
> 3. **Krylov Subspace**: PBiCGStab ทำงานใน Krylov subspace เพื่อลดจำนวน iterations

---

## 2. การจัดการหน่วยความจำและ I/O

### 2.1 การจัดการหน่วยความจำ (Memory Management)

ในการจำลองขนานใหญ่ หน่วยความจำต่อโปรเซสเซอร์ (Memory per core) เป็นข้อจำกัดที่สำคัญ

#### 2.1.1 Memory Estimation

$$ \text{Memory Requirement} \approx N_{\text{cells}} \times N_{\text{fields}} \times N_{\text{bytes}} \times \text{overhead} $$

โดยที่:
- $N_{\text{cells}}$ คือ จำนวนเซลล์ต่อ processor
- $N_{\text{fields}}$ คือ จำนวนฟิลด์ (p, U, k, epsilon, etc.)
- $N_{\text{bytes}}$ คือ 4 (float) หรือ 8 (double)
- $\text{overhead}$ คือ 2-3 (mesh connectivity, communication buffers)

#### 2.1.2 Compressed Storage

```cpp
// NOTE: Synthesized by AI - Verify parameters
// Memory management and compression in controlDict
application     simpleFoam;

startFrom       latestTime;

startTime       0;

stopAt          endTime;

endTime         1000;

deltaT          1;

writeControl    timeStep;

writeInterval   100;

// Enable data compression
writeCompression    on;   // Use gzip compression
// Or specify compression level
writeCompression    true;
compressionLevel    6;    // 0-9 (default: 6)

// Disable writing of some fields to save space
// (Must be specified in fields section)
```

> 📂 **Source:** `.src/OpenFOAM/db/IOobject/IOobject.C`

> **คำอธิบาย (Thai Explanation):**
> การจัดการหน่วยความจำและการบีบอัดข้อมูลใน OpenFOAM:
> - **writeCompression**: เปิดใช้งาน gzip compression สำหรับไฟล์ output ซึ่งลดขนาดไฟล์ลง 70-90%
> - **compressionLevel**: ระดับการบีบอัด 0 (ไม่บีบอัด) ถึง 9 (บีบอัดสูงสุด, ใช้เวลานาน)
> - **Trade-off**: การบีบอัดสูงลด disk space แต่เพิ่มเวลา I/O
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Lossless Compression**: gzip ใช้ lossless compression ดังนั้นข้อมูลจะไม่สูญหาย
> 2. **Binary vs ASCII**: Binary files มักจะเล็กกว่าและเร็วกว่า ASCII
> 3. **Sparse Fields**: Fields ที่มีค่าสม่ำเสมอ (smooth) บีบอัดได้ดีกว่า

> [!INFO] **การประหยัดพื้นที่ดิสก์**
> `writeCompression on;` ใน `controlDict` ช่วยลดขนาดไฟล์ลงได้ถึง 70-90% สำหรับฟิลด์ที่มีความสม่ำเสมอ (smooth fields) สำหรับ cases ขนาดใหญ่ compression level 6-9 แนะนำ แต่จะใช้เวลาในการเขียนมากขึ้น

#### 2.1.3 Write Management

```cpp
// NOTE: Synthesized by AI - Verify parameters
// Optimal data writing strategies
writeControl    runTime;      // Write based on simulation time
writeInterval   10;           // Write every 10 simulation seconds

// Or use adjustedRunTime for transient cases
writeControl    adjustedRunTime;
writeInterval   10;
timeFormat      general;
timePrecision   6;

// Or use cpuTime for monitoring
writeControl    cpuTime;
writeInterval   3600;         // Write every 1 CPU hour

// Writing only certain time steps
writeControl    timeStep;
writeInterval   100;
purgeWrite      5;            // Keep only last 5 time directories
```

> 📂 **Source:** `.src/OpenFOAM/db/Time/Time.C`

> **คำอธิบาย (Thai Explanation):**
> กลยุทธ์การเขียนข้อมูลที่เหมาะสมเพื่อการจัดการดิสก์และ I/O:
> - **writeControl**: กำหนดเงื่อนไขการเขียน (timeStep, runTime, adjustedRunTime, cpuTime)
> - **purgeWrite**: ลบ time directories เก่าๆ โดยเก็บเฉพาะจำนวนที่ระบุ
> - **adjustedRunTime**: ปรับเวลา output ให้สอดคล้องกับ writeInterval
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **I/O Bottleneck**: การเขียนข้อมูลบ่อยๆ ลดประสิทธิภาพของ simulation
> 2. **Storage Management**: purgeWrite ช่วยจัดการ disk space อัตโนมัติ
> 3. **Monitoring**: cpuTime control ช่วยในการ estimate ระยะเวลา simulation

#### 2.1.4 Selective Field Writing

```cpp
// NOTE: Synthesized by AI - Verify parameters
// In controlDict - write only necessary fields
// Must use function objects
functions
{
    writeSelectedFields
    {
        type            sets;
        functionObjectLibs ("libsampling.so");
        enabled         true;
        writeControl    timeStep;
        writeInterval   50;

        sets
        (
            monitorLine
            {
                type            uniform;
                axis            distance;
                start           (0 0 0);
                end             (1 0 0);
                nPoints         100;
            }
        );

        fields
        (
            p
            U
            k
            epsilon
        );
    }
}
```

> 📂 **Source:** `.src/sampling/sampledSet/sampledSet.C`

> **คำอธิบาย (Thai Explanation):**
> การเขียนเฉพาะฟิลด์ที่จำเป็นโดยใช้ function objects:
> - **sets**: Function object สำหรับ sampling fields บน lines/planes
> - **monitorLine**: กำหนดเส้นที่ต้องการ sample ข้อมูล
> - **fields**: ระบุเฉพาะ fields ที่ต้องการเก็บ
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Selective Output**: ลด I/O โดยการเขียนเฉพาะข้อมูลที่สำคัญ
> 2. **Sampling Points**: กำหนดจุดหรือเส้นที่ต้องการติดตามค่า
> 3. **Function Objects**: กลไกของ OpenFOAM ในการทำ post-processing ระหว่าง simulation

### 2.2 การเพิ่มประสิทธิภาพ I/O (I/O Optimization)

การเขียนข้อมูลลงดิสก์พร้อมกันจากหลายโปรเซสเซอร์มักเกิดปัญหาคอขวด

#### 2.2.1 Parallel I/O Strategies

```mermaid
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Parallel Simulation]:::explicit --> B{I/O Strategy}:::explicit
B --> C[Master Process I/O]:::implicit
B --> D[Collective I/O]:::implicit
B --> E[Independent I/O]:::implicit
C --> C1[Pros: Simple<br>Cons: Serial bottleneck]:::context
D --> D1[Pros: High Perf<br>Cons: Needs Parallel FS]:::context
E --> E1[Pros: Scalable<br>Cons: Complex Mgmt]:::context
```
> **Figure 1:** แผนผังกลยุทธ์การจัดการ I/O ในการจำลองแบบขนาน เปรียบเทียบระหว่างการเขียนข้อมูลผ่าน Master Process, การเขียนแบบรวมกลุ่ม (Collective) และการเขียนแบบอิสระ (Independent) พร้อมข้อดีและข้อเสียในแต่ละรูปแบบ

#### 2.2.2 Optimizing Decomposition for I/O

```cpp
// NOTE: Synthesized by AI - Verify parameters
// In decomposeParDict - settings to reduce I/O bottleneck
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}

// Use Scotch for best load balancing
method          scotch;
// Or if you want manual control
// method          hierarchical;

// Settings for hierarchical
coeffs
{
    n           (4 2 1);     // Decompose along x-direction first
}

// Or settings for scotch
coeffs
{
    // Scotch-specific options
    processorWeights  (1 1 1 1);  // Equal weights for all processors
    strategy "edge";              // "edge", "vertex", "band"
}

// Number of subdomains
numberOfSubdomains  16;

// Don't write decomposition visualization
writeDecomposition    no;
```

> 📂 **Source:** `.applications/utilities/parallelProcessing/decomposePar/decomposePar.C`

> **คำอธิบาย (Thai Explanation):**
> การตั้งค่า decomposition เพื่อลดปัญหา I/O bottleneck:
> - **scotch**: Graph-based decomposition method ที่ให้ load balancing ที่ดีที่สุด
> - **strategy "edge"**: ลด edge cuts ซึ่งช่วยลด communication ระหว่าง processors
> - **processorWeights**: ระบุน้ำหนักสำหรับ heterogeneous systems
> - **writeDecomposition**: ปิดการเขียนไฟล์ visualization เพื่อประหยัด I/O
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Domain Decomposition**: แบ่ง mesh เป็น subdomains สำหรับ parallel processing
> 2. **Graph Partitioning**: Scotch ใช้ graph theory ในการ minimize communication
> 3. **Edge Cuts**: จำนวน faces ระหว่าง subdomains ซึ่งส่งผลต่อ communication overhead

> [!TIP] **I/O Optimization Tips**
> - **Parallel I/O**: ใช้เครื่องมือ I/O แบบขนานหากระบบไฟล์รองรับ (Lustre, GPFS, BeeGFS)
> - **Write Interval**: เพิ่ม `writeInterval` เพื่อลดความถี่ในการเขียน
> - **Fields to Write**: ระบุเฉพาะฟิลด์ที่จำเป็น
> - **Compression**: ใช้ `writeCompression on;` และ `compressionLevel 6;`
> - **Purge Old Data**: ใช้ `purgeWrite` เพื่อลบ time directories เก่า

#### 2.2.3 Collated I/O (Newer OpenFOAM versions)

```cpp
// NOTE: Synthesized by AI - Verify parameters
// In controlDict - use Collated I/O for better performance
// OpenFOAM v1612+ or v+

// Using collated file format
writeFormat      binary;
writePrecision   6;

// Collated I/O settings (OpenFOAM v1806+)
ioRanks          4;        // Number of I/O aggregators
writeJobMode     collective; // Or "masterOnly" or "distributed"
```

> 📂 **Source:** `.src/OpenFOAM/db/IOstreams/collated`

> **คำอธิบาย (Thai Explanation):**
> Collated I/O เป็นวิธีการรวบรวม I/O operations จากหลาย processors:
> - **ioRanks**: จำนวน processors ที่ทำหน้าที่เป็น I/O aggregators
> - **collective**: รูปแบบ I/O แบบรวมกลุ่มที่เหมาะสำหรับ parallel file systems
> - **masterOnly**: เขียนผ่าน master process เท่านั้น (ใช้เมื่อ file system ไม่รองรับ parallel I/O)
> - **distributed**: แต่ละ processor เขียนข้อมูลเอง (ใช้เมื่อมี disk แยกสำหรับแต่ละ node)
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **I/O Aggregation**: รวมหลาย small writes เป็น fewer large writes
> 2. **Two-Phase I/O**: Phase 1 - gather data, Phase 2 - write to disk
> 3. **File System Compatibility**: ต้องเลือกโหมดที่เหมาะกับ file system

---

## 3. เวิร์กโฟลว์แบบขนานแบบครบวงจร

### 3.1 ขั้นตอนการจำลองแบบขนาน

```mermaid
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Setup]:::context --> B[Mesh]:::explicit
B --> C[Check]:::explicit
C --> D{OK?}:::explicit
D -->|No| B
D -->|Yes| E[Decompose]:::implicit
E --> F[Run]:::implicit
F --> G[Monitor]:::explicit
G --> H{Done?}:::explicit
H -->|No| F
H -->|Yes| I[Reconstruct]:::implicit
I --> J[Post]:::context
J --> K[Vis]:::context
```
> **Figure 2:** ขั้นตอนการจำลองแบบขนานแบบครบวงจร ตั้งแต่การเตรียมเคส การสร้างและตรวจสอบเมช การย่อยโดเมน การรัน Solver พร้อมติดตามประสิทธิภาพ ไปจนถึงการรวมผลลัพธ์และแสดงผลภาพ

### 3.2 ตัวอย่าง Workflow Script

```bash
#!/bin/bash
# NOTE: Synthesized by AI - Test thoroughly before production use
# parallelFoamRun.sh - Complete Parallel Workflow

# ============================================
# OpenFOAM Parallel Run Script
# ============================================

# 1. Clean case (optional)
echo "Cleaning case..."
foamCleanTutorials

# 2. Generate mesh
echo "Generating mesh..."
blockMesh > log.blockMesh 2>&1

# 3. Check mesh quality
echo "Checking mesh quality..."
checkMesh > log.checkMesh 2>&1

# Extract mesh statistics
if grep -q "Mesh OK" log.checkMesh; then
    echo "Mesh quality check passed!"
else
    echo "WARNING: Mesh quality issues detected!"
    echo "Check log.checkMesh for details"
fi

# 4. Decompose domain
echo "Decomposing domain for parallel processing..."
NPROCS=4  # Number of processors
decomposePar -celldist -decomposeParDict system/decomposeParDict > log.decomposePar 2>&1

# 5. Run solver in parallel
echo "Running solver in parallel on $NPROCS processors..."
mpirun -np $NPROCS simpleFoam -parallel > log.simpleFoam 2>&1

# 6. Reconstruct results
echo "Reconstructing results..."
reconstructPar > log.reconstructPar 2>&1

# 7. Post-processing example
echo "Running post-processing..."
paraFoam -builtin &

echo "Simulation complete!"
```

> 📂 **Source:** `.applications/utilities/parallelProcessing/decomposePar`

> **คำอธิบาย (Thai Explanation):**
> สคริปต์สำหรับ workflow การจำลองแบบขนานแบบครบวงจร:
> - **foamCleanTutorials**: ลบข้อมูลเก่าจากการรันครั้งก่อน
> - **blockMesh**: สร้าง mesh จาก blockMeshDict
> - **checkMesh**: ตรวจสอบคุณภาพของ mesh
> - **decomposePar**: แบ่ง domain เป็น subdomains สำหรับ parallel processing
> - **mpirun**: รัน solver แบบขนานด้วย MPI
> - **reconstructPar**: รวมผลลัพธ์จาก processors กลับเป็น single domain
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Pipeline**: ทุกขั้นตอนต้องเสร็จสิ้นก่อนดำเนินการต่อ
> 2. **Error Checking**: ตรวจสอบผลลัพธ์จากแต่ละขั้นตอน
> 3. **Log Files**: เก็บ log ไว้ตรวจสอบและ debug

### 3.3 Advanced Workflow with Error Handling

```bash
#!/bin/bash
# NOTE: Synthesized by AI - Test thoroughly before production use
# advancedParallelRun.sh - Workflow with error handling and monitoring

# Configuration
CASE_DIR=$(pwd)
NPROCS=16
SOLVER="simpleFoam"
LOG_DIR="$CASE_DIR/logs"

# Create log directory
mkdir -p $LOG_DIR

# Function for error handling
check_error() {
    if [ $? -ne 0 ]; then
        echo "ERROR: $1 failed!"
        exit 1
    fi
}

# Step 1: Mesh generation
echo "=== Step 1: Mesh Generation ==="
blockMesh 2>&1 | tee $LOG_DIR/log.blockMesh
check_error "blockMesh"

# Step 2: Mesh quality check
echo "=== Step 2: Mesh Quality Check ==="
checkMesh -allGeometry -allTopology 2>&1 | tee $LOG_DIR/log.checkMesh

# Step 3: Decomposition
echo "=== Step 3: Domain Decomposition ==="
decomposePar -celldist 2>&1 | tee $LOG_DIR/log.decomposePar
check_error "decomposePar"

# Step 4: Check decomposition balance
echo "=== Checking load balance ==="
grep "cells per processor" $LOG_DIR/log.decomposePar

# Step 5: Parallel run
echo "=== Step 4: Parallel Solver Run ==="
echo "Starting $SOLVER on $NPROCS processors..."
mpirun -np $NPROCS $SOLVER -parallel 2>&1 | tee $LOG_DIR/log.$SOLVER

# Monitor convergence in real-time (optional)
# tail -f $LOG_DIR/log.$SOLVER | grep "Solve for p"

# Step 6: Reconstruct
echo "=== Step 5: Reconstruct Results ==="
reconstructPar -latestTime 2>&1 | tee $LOG_DIR/log.reconstructPar
check_error "reconstructPar"

# Step 7: Performance summary
echo "=== Performance Summary ==="
grep "ExecutionTime" $LOG_DIR/log.$SOLVER | tail -1

echo "Simulation completed successfully!"
```

> 📂 **Source:** `.applications/utilities/parallelProcessing/decomposePar/decomposePar.C`

> **คำอธิบาย (Thai Explanation):**
> สคริปต์ขั้นสูงที่มีการจัดการ error และ monitoring:
> - **check_error Function**: ตรวจสอบ return code จากแต่ละคำสั่ง
> - **Log Directory**: แยก log files ไว้ใน directory เฉพาะ
> - **tee Command**: แสดงผลทั้งบนหน้าจอและบันทึกลงไฟล์
> - **Performance Summary**: สรุปเวลา execution ในตอนท้าย
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Error Handling**: หยุดการทำงานทันทีหากมีขั้นตอนล้มเหลว
> 2. **Logging**: เก็บ logs ทุกขั้นตอนสำหรับ debugging
> 3. **Load Balance Check**: ตรวจสอบความสมดุลของ workload
> 4. **Real-time Monitoring**: สามารถติดตาม residuals ได้แบบ real-time

---

## 4. Advanced Optimization Techniques

### 4.1 การปรับแต่ง Algorithmic

#### 4.1.1 Under-Relaxation Factors

ใน `fvSolution`, การปรับ Under-Relaxation Factors สามารถช่วยเพิ่มเสถียรภาพของการคำนวณ:

$$ \phi^{(n+1)} = \phi^{(n)} + \alpha \left( \phi^* - \phi^{(n)} \right) $$

โดยที่:
- $\phi^{(n+1)}$ คือ ค่าใหม่ที่จะใช้ใน iteration ถัดไป
- $\phi^{(n)}$ คือ ค่าจาก iteration ก่อนหน้า
- $\phi^*$ คือ ค่าใหม่ที่คำนวณได้จาก solver
- $\alpha \in (0, 1]$ คือ Under-relaxation factor

สำหรับระบบ non-linear การเลือก $\alpha$ ที่เหมาะสมมีความสำคัญ:

$$ \alpha_{\text{optimal}} \approx \frac{2}{2 - \lambda_{\text{min}} - \lambda_{\text{max}}} $$

โดยที่ $\lambda$ คือ eigenvalues ของ Jacobian matrix

```cpp
// NOTE: Synthesized by AI - Verify parameters
// Under-Relaxation Factors settings in fvSolution
relaxationFactors
{
    fields
    {
        p               0.3;    // Pressure relaxation (conservative)
        rho             0.05;   // Density relaxation (compressible - very conservative)
        pFinal          0.3;    // Final pressure relaxation
    }
    equations
    {
        U               0.7;    // Momentum relaxation
        "(k|epsilon|omega)"   0.8;    // Turbulence relaxation
        nuTilda         0.8;    // Spalart-Allmaras relaxation
    }
}

// For PIMPLE algorithm
PIMPLE
{
    // Dynamic relaxation factors
    consistent      yes;     // Use consistent formulation
}
```

> 📂 **Source:** `.applications/solvers/incompressible/simpleFoam/simpleFoam.C`

> **คำอธิบาย (Thai Explanation):**
> Under-Relaxation Factors ใช้เพื่อเพิ่มความเสถียรของการแก้สมการ non-linear:
> - **fields**: Relaxation factors สำหรับ fields (pressure, density)
> - **equations**: Relaxation factors สำหรับ equations (momentum, turbulence)
> - **consistent**: ใช้ consistent formulation สำหรับ PIMPLE เพื่อความเสถียรที่ดีขึ้น
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Relaxation**: ลดการเปลี่ยนแปลงของ solution ระหว่าง iterations
> 2. **Stability vs Convergence**: Factor ต่ำ = เสถียรกว่า แต่ลู่เข้าช้ากว่า
> 3. **Pressure Coupling**: Pressure มักต้องการ factor ต่ำกว่า velocity

> [!INFO] **Under-Relaxation Best Practices**
> - **Steady-state**: $\alpha_p = 0.3$, $\alpha_U = 0.7$ เป็นค่าเริ่มต้นที่ดี
> - **Transient**: $\alpha$ สามารถเพิ่มได้เนื่องจาก time step มีผลในการ stabilize
> - **Difficult cases**: ลด $\alpha$ ถ้าการคำนวณ diverge
> - **Fast convergence**: เพิ่ม $\alpha$ ถ้าการคำนวณ converge ไวเกินไป

#### 4.1.2 High-Resolution Schemes

เพื่อหลีกเลี่ยงปัญหา numerical diffusion และ maintain stability:

```cpp
// NOTE: Synthesized by AI - Verify parameters
// High-Resolution Schemes in fvSchemes
ddtSchemes
{
    default         Euler;  // For steady-state
    // Or backward for transient accuracy
}

gradSchemes
{
    default         Gauss linear;
    grad(p)         Gauss linear;
    grad(U)         Gauss linear;
}

divSchemes
{
    default         none;

    // Convection schemes - High resolution
    div(phi,U)      Gauss limitedLinearV 1;  // TVD scheme for momentum
    div(phi,k)      Gauss limitedLinear 1;
    div(phi,epsilon) Gauss limitedLinear 1;
    div(phi,omega)  Gauss limitedLinear 1;

    // For compressible flow
    div(phi,U)      Gauss upwind;  // More robust for compressible

    // For VOF (interFoam)
    div(phi,alpha)  Gauss vanLeer;   // Compressive scheme
    div(phirb,alpha) Gauss interfaceCompression 1;
}

laplacianSchemes
{
    default         Gauss linear corrected;
    laplacian(nu,U) Gauss linear corrected;
    laplacian(1,p)  Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}
```

> 📂 **Source:** `.src/finiteVolume/interpolation/schemes`

> **คำอธิบาย (Thai Explanation):**
> Numerical Schemes สำหรับการ discretize สมการ:
> - **limitedLinearV**: TVD (Total Variation Diminishing) scheme สำหรับ convection
> - **vanLeer**: Flux limiter scheme สำหรับ VOF methods
> - **interfaceCompression**: Scheme พิเศษสำหรับรักษาความชัดเจนของ interface
> - **corrected**: การแก้ไข non-orthogonality ใน laplacian schemes
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Numerical Diffusion**: Upwind schemes มี diffusion สูง, linear schemes มี oscillations
> 2. **TVD Schemes**: ลด diffusion และป้องกัน oscillations
> 3. **Flux Limiters**: จำกัด flux เพื่อป้องกัน non-physical overshoots

#### 4.1.3 Non-Orthogonal Correction

สำหรับ mesh ที่มี non-orthogonality สูง:

$$ \nabla \phi_f = \mathbf{g} + (\mathbf{n} \cdot \nabla \phi_f - \mathbf{n} \cdot \mathbf{g})\mathbf{n} $$

โดยที่:
- $\mathbf{g}$ คือ explicit gradient ที่หน้าเซลล์
- $\mathbf{n}$ คือ normal vector ที่หน้าเซลล์

```cpp
// NOTE: Synthesized by AI - Verify parameters
// Settings for non-orthogonal mesh
laplacianSchemes
{
    default         Gauss linear uncorrected;  // If non-orthogonality < 70°
    // Or
    default         Gauss linear corrected;    // If non-orthogonality < 80°
    // Or
    default         Gauss linear limited 0.5;  // If non-orthogonality very high
}

// In fvSolution - non-orthogonal correctors
simple
{
    nNonOrthogonalCorrectors 3;  // Increase if mesh has high non-orthogonality
}
```

> 📂 **Source:** `.src/finiteVolume/finiteVolume/lnInclude`

> **คำอธิบาย (Thai Explanation):**
> การจัดการกับ non-orthogonal meshes:
> - **uncorrected**: ไม่มีการแก้ไข non-orthogonality (เร็วแต่ไม่แม่นยำ)
> - **corrected**: มีการแก้ไข non-orthogonality (แม่นยำแต่ช้ากว่า)
> - **limited**: จำกัดการแก้ไขเพื่อความเสถียร
> - **nNonOrthogonalCorrectors**: จำนวนรอบการแก้ไขแต่ละ time step
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Non-Orthogonality**: มุมระหว่าง face normal และ line connecting cell centers
> 2. **Explicit Correction**: คำนวณ correction term แยกจาก implicit term
> 3. **Iterative Solution**: ต้องการ multiple correctors สำหรับ high non-orthogonality

### 4.2 การปรับแต่ง Mesh Decomposition

#### 4.2.1 Decomposition Methods Comparison

| Method | Description | Best For | Performance | Complexity |
|--------|-------------|----------|-------------|------------|
| `simple` | ตัดตามทิศทาง Cartesian | Mesh สี่เหลี่ยม, รูปทรงเรขาคณิตง่าย | กลาง | ต่ำ |
| `hierarchical` | ตัดตามลำดับชั้น (recursive) | Mesh ปกติทั่วไป | ดี | กลาง |
| `scotch` | Graph-based (recommended) | Complex geometry | ดีมาก | กลาง |
| `metis` | Graph-based (legacy) | Complex geometry | ดี | กลาง |
| `manual` | ผู้ใช้ระบุเอง | Testing/Debugging | แปรผัน | สูง |
| `ptScotch` | Parallel graph decomposition | Very large cases | ดีที่สุด | สูง |

#### 4.2.2 Load Balancing Metrics

$$ \text{Load Balance Ratio} = \frac{N_{\text{max}}}{N_{\text{avg}}} $$

โดยที่:
- $N_{\text{max}}$ คือ จำนวนเซลล์สูงสุดใน processor ใดๆ
- $N_{\text{avg}}$ คือ จำนวนเซลล์เฉลี่ยต่อ processor

ค่าที่ดี: Load Balance Ratio < 1.1

$$ \text{Parallel Efficiency} \approx \frac{1}{\text{Load Balance Ratio}} $$

```cpp
// NOTE: Synthesized by AI - Verify parameters
// Scotch settings for optimal Load Balancing
decomposeParDict
{
    method          scotch;

    coeffs
    {
        // Scotch-specific options
        strategy "edge";       // "edge", "vertex", "band"
        // edge: minimize edge cuts (best for communication)
        // vertex: balance cell count
        // band: minimize bandwidth

        weight 1000;           // Balance weight (higher = more important)

        // Advanced options
        // displayStats    yes;    // Show decomposition statistics
        // writeDecomposition    no; // Don't write decomposition file
    }

    // Number of subdomains
    numberOfSubdomains  16;

    // Optional: specify processor weights for heterogeneous systems
    // processorWeights (1.0 1.0 1.0 1.0);

    // Output decomposition for visualization
    writeDecomposition    no;
}
```

> 📂 **Source:** `.applications/utilities/parallelProcessing/decomposePar/decomposePar.C`

> **คำอธิบาย (Thai Explanation):**
> การตั้งค่า Scotch decomposition method:
> - **strategy "edge"**: ลด edge cuts ซึ่งลด communication ระหว่าง processors
> - **weight**: น้ำหนักที่ให้กับ load balancing เทียบกับ communication minimization
> - **numberOfSubdomains**: จำนวน subdomains ที่ต้องการ (ควรเท่ากับจำนวน cores)
> - **processorWeights**: ใช้สำหรับ heterogeneous systems ที่มี cores ที่ต่างกัน
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Graph Partitioning**: แทน mesh ด้วย graph แล้วแบ่งเป็น subgraphs
> 2. **Load Balance**: แต่ละ processor ควรมีจำนวนเซลล์ใกล้เคียงกัน
> 3. **Communication Minimization**: ลด interface ระหว่าง subdomains

> [!TIP] **Load Balancing Metrics**
> ตรวจสอบความสมดุลของการโหลดงานโดยใช้:
> ```bash
> decomposePar -cellDist
> # ตรวจสอบ log.decomposePar สำหรับ "per cell" statistics
> # หรือใช้ pyFoam:
> pyFoamPlotRunner.py log.simpleFoam
> ```

#### 4.2.3 Communication Minimization

สำหรับ hierarchical decomposition:

```cpp
// NOTE: Synthesized by AI - Verify parameters
// Settings to minimize communication
method          hierarchical;

coeffs
{
    n   (4 2 2);  // 4x2x2 = 16 processors

    // Decomposition order: x, y, z
    // Choose direction with longest dimension first
    // To reduce surface-to-volume ratio
}

// Or use manual decomposition
method          manual;

manualCoeffs
{
    processor1
    {
        boundingBox (0 0 0) (1 1 1);
    }
    processor2
    {
        boundingBox (1 0 0) (2 1 1);
    }
    // ... continue for all processors
}
```

> 📂 **Source:** `.src/OpenFOAM/db/decomposition/decompositionMethod`

> **คำอธิบาย (Thai Explanation):**
> การลด communication โดยการเลือก decomposition order:
> - **hierarchical**: แบ่ง domain ตามลำดับชั้น (recursive)
> - **n (4 2 2)**: แบ่งตาม x-direction เป็น 4 ส่วน, y-direction เป็น 2 ส่วน, z-direction เป็น 2 ส่วน
> - **manual**: ผู้ใช้ระบุ bounding box สำหรับแต่ละ processor
> - **Surface-to-Volume Ratio**: ค่าน้อย = ลด communication
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Decomposition Order**: เริ่มจากทิศทางที่ยาวที่สุด
> 2. **Aspect Ratio**: Subdomains ควรมี aspect ratio ใกล้เคียง 1
> 3. **Interface Area**: ลดพื้นที่ผิวระหว่าง subdomains

### 4.3 Profiling and Performance Analysis

#### 4.3.1 Built-in Profiling

```cpp
// NOTE: Synthesized by AI - Verify parameters
// In controlDict - enable Profiling
libs
(
    "libprofilingSo.so"
);

profiling
{
    active          true;
    writeInterval   10;
    timeFormat      general;
    timePrecision   6;

    // Profile specific operations
    profileSolvers  yes;
    profileCourant  yes;

    // Output format
    file            "profiling.dat";
}
```

> 📂 **Source:** `.src/OSspecific/POSIX/profiling`

> **คำอธิบาย (Thai Explanation):**
> การเปิดใช้งาน profiling ในตัวของ OpenFOAM:
> - **libs**: Load profiling library
> - **profileSolvers**: บันทึกเวลาที่ solvers ใช้
> - **profileCourant**: บันทึกค่า Courant number
> - **writeInterval**: ความถี่ในการเขียน profiling data
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Function Profiling**: วัดเวลาที่ใช้ในแต่ละ function
> 2. **Solver Analysis**: เปรียบเทียบเวลาของ pressure vs momentum solvers
> 3. **Performance Bottlenecks**: ระบุส่วนที่ใช้เวลานานที่สุด

#### 4.3.2 System Profiling Tools

```bash
# NOTE: Synthesized by AI - Verify commands for your system
# Use time command to measure performance
/usr/bin/time -v mpirun -np 16 simpleFoam -parallel

# Or use perf (Linux)
perf stat -e cache-references,cache-misses,instructions,cycles mpirun -np 16 simpleFoam -parallel

# Or Intel VTune (if available)
vtune -collect hotspots -result-dir vtune_results mpirun -np 16 simpleFoam -parallel

# Or Scalasca (MPI profiling)
scan -s mpirun -np 16 simpleFoam -parallel
export SCAN_REPORT=profiling_report
sqpost -f profiling_report

# Or Score-P
scorep --nocompiler --thread=pthread --mpp=mpi mpirun -np 16 simpleFoam -parallel
scorep-score -r profile.cubex
```

> 📂 **Source:** `.doc/compilation/ThirdParty`

> **คำอธิบาย (Thai Explanation):**
> เครื่องมือวิเคราะห์ประสิทธิภาพภายนอก OpenFOAM:
> - **time**: Built-in Linux command สำหรับวัด execution time
> - **perf**: Linux performance analysis tool สำหรับ hardware counters
> - **VTune**: Intel's tool สำหรับ hotspot analysis
> - **Scalasca**: Tool สำหรับ MPI profiling
> - **Score-P**: มาตรฐาน profiling tool สำหรับ HPC applications
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Hardware Counters**: Cache misses, instructions, cycles
> 2. **MPI Tracing**: วิเคราะห์ communication patterns
> 3. **Hotspots**: ระบุ code sections ที่ใช้เวลานานที่สุด

#### 4.3.3 Performance Metrics

$$ \text{Speedup} = S_p = \frac{T_1}{T_p} $$

$$ \text{Parallel Efficiency} = E_p = \frac{S_p}{p} = \frac{T_1}{p \cdot T_p} $$

$$ \text{Serial Fraction} = f_s = \frac{1/p - E_p}{1/E_p - 1} $$

โดยที่:
- $T_1$ คือ เวลาบน 1 processor
- $T_p$ คือ เวลาบน $p$ processors
- $S_p$ คือ Speedup บน $p$ processors
- $E_p$ คือ Parallel efficiency (ideal = 1.0)

Amdahl's Law:
$$ S_p = \frac{1}{f_s + \frac{1 - f_s}{p}} $$

Gustafson's Law:
$$ S_p = p - f_s (p - 1) $$

> [!INFO] **Interpreting Performance Metrics**
> - **Speedup > 0.7p**: Excellent parallelization (70%+ efficiency)
> - **Speedup 0.5-0.7p**: Good parallelization (50-70% efficiency)
> - **Speedup < 0.5p**: Poor parallelization (< 50% efficiency)
> - **Serial fraction > 0.1**: Indicates significant serial bottlenecks

#### 4.3.4 Communication Analysis

```bash
# Use mpiP for MPI profiling
mpirun -np 16 mpiP -mpip mpirun -np 16 simpleFoam -parallel

# Or Intel Trace Analyzer
mpirun -np 16 -trace simpleFoam -parallel
mpi2prv -f simpleFoam.prv -o simpleFoam.prv

# Analyze what you get:
# - MPI_Send, MPI_Recv number of times and time
# - MPI_Barrier waiting time
# - Load imbalance between processors
```

> 📂 **Source:** `.src/Pstream/mpi`

> **คำอธิบาย (Thai Explanation):**
> เครื่องมือสำหรับวิเคราะห์ MPI communication:
> - **mpiP**: Lightweight MPI profiling library
> - **Intel Trace Analyzer**: Tool สำหรับ visualization ของ MPI communication
> - **MPI_Send/Recv**: วัดปริมาณและเวลาของ message passing
> - **MPI_Barrier**: วัดเวลาที่ processors รอกัน
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Communication Patterns**: Point-to-point vs Collective communication
> 2. **Synchronization**: Barriers ทำให้ processors รอกัน
> 3. **Load Imbalance**: Processors บางตัวทำงานนานกว่า

---

## 5. Troubleshooting Common Issues

### 5.1 Memory Issues

> [!WARNING] **Out of Memory Errors**
> หากเกิดปัญหาเรื่องหน่วยความจำ:
> 1. ลดจำนวน processors (เพิ่ม memory per core)
> 2. เปิดใช้ `writeCompression on`
> 3. ลด `writeInterval`
> 4. ใช้ `foamListTimes` เพื่อลบ time directories ที่ไม่จำเป็น
> 5. ลดจำนวน fields ที่เก็บใน memory

**Memory Profiling:**
```bash
# Check memory usage during simulation
/usr/bin/time -v mpirun -np 16 simpleFoam -parallel 2>&1 | grep "Maximum resident"

# Or use valgrind
mpirun -np 16 valgrind --tool=massif --massif-out-file=massif.out simpleFoam -parallel
ms_print massif.out | less
```

> 📂 **Source:** `.src/OpenFOAM/db/IOobject`

> **คำอธิบาย (Thai Explanation):**
> การวินิจฉัยและแก้ไขปัญหาหน่วยความจำ:
> - **Maximum resident**: หน่วยความจำสูงสุดที่ใช้
> - **valgrind massif**: Tool สำหรับ heap profiling
> - **ms_print**: แสดงผล memory usage เป็น graph
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Memory per Core**: จำกัดของ RAM ต่อ CPU core
> 2. **Memory Leaks**: การจองหน่วยความจำโดยไม่คืน
> 3. **Peak Memory**: ช่วงเวลาที่ใช้หน่วยความจำมากที่สุด

### 5.2 Convergence Issues

> [!WARNING] **Non-Converging Solutions**
> สำหรับปัญหาการลู่เข้า:
> 1. ลด Under-relaxation factors (เริ่มจาก 0.3 สำหรับ pressure)
> 2. เพิ่ม Solver iterations (`maxIter`)
> 3. ตรวจสอบ Mesh quality (`checkMesh`)
> 4. ลด `deltaT` สำหรับ transient cases
> 5. ใช้ robust schemes (upwind แทน linear)

**Convergence Monitoring:**
```bash
# Check residuals real-time
tail -f log.simpleFoam | grep "Solve for p"

# Or use pyFoam
pyFoamPlotRunner.py log.simpleFoam
```

> 📂 **Source:** `.applications/solvers/incompressible/simpleFoam`

> **คำอธิบาย (Thai Explanation):**
> การวินิจฉัยและแก้ไขปัญหาการลู่เข้า:
> - **Residuals**: ค่า error ของสมการแต่ละ iteration
> - **Relaxation**: ลดการเปลี่ยนแปลงเพื่อเพิ่มความเสถียร
> - **Mesh Quality**: Mesh ที่ไม่ดีทำให้ไม่ลู่เข้า
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Divergence**: Residuals เพิ่มขึ้นแทนที่จะลดลง
> 2. **Oscillation**: Residuals สั่นไปมา
> 3. **Stagnation**: Residuals ไม่ลดลงต่ำ

### 5.3 Speedup Issues

> [!INFO] **Poor Parallel Scaling**
> ตรวจสอบ Parallel Efficiency:
> $$ E_p = \frac{S_p}{p} = \frac{T_1}{p \cdot T_p} $$
>
> สาเหตุทั่วไป:
> 1. **Serial bottleneck**: I/O ไม่ได้ทำแบบขนาน
> 2. **Load imbalance**: Decomposition ไม่ดี
> 3. **Communication overhead**: ใช้ processors มากเกินไป
> 4. **Cache effects**: Cache misses เพิ่มขึ้น

**Diagnostic Commands:**
```bash
# Check load balance
decomposePar -celldist
grep "cells" log.decomposePar

# Check scaling
# Run on 1, 2, 4, 8, 16 processors
# Compare ExecutionTime in log files
```

> 📂 **Source:** `.applications/utilities/parallelProcessing/decomposePar`

> **คำอธิบาย (Thai Explanation):**
> การวินิจฉัยปัญหา scaling:
> - **Serial Bottleneck**: ส่วนที่ไม่สามารถ parallelize ได้
> - **Load Imbalance**: Processors บางตัวมีงานมากกว่า
> - **Communication Overhead**: เวลาที่เสียไปกับการส่งข้อมูล
> - **Cache Effects**: การแบ่งข้อมูลทำให้ cache ไม่มีประสิทธิภาพ
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Amdahl's Law**: ขีดจำกัดของ speedup ขึ้นกับ serial fraction
> 2. **Strong Scaling**: ขนาดปัญหาคงที่, เพิ่ม processors
> 3. **Weak Scaling**: เพิ่มทั้งปัญหาและ processors ตามสัดส่วน

### 5.4 I/O Bottlenecks

> [!WARNING] **Slow I/O Performance**
> แก้ไข I/O bottlenecks:
> 1. ใช้ `writeCompression on`
> 2. เพิ่ม `writeInterval`
> 3. ใช้ Parallel File System หากมี
> 4. ลดจำนวน fields ที่เขียน
> 5. ใช้ `collated` I/O (OpenFOAM v1806+)

### 5.5 Decomposition Issues

> [!WARNING] **Poor Decomposition**
> สัญญาณของ decomposition ที่ไม่ดี:
> 1. Load balance ratio > 1.2
> 2. บาง processors ทำงานนานกว่า others
> 3. Communication overhead สูง

**Solution:**
```bash
# Try different decomposition methods
# 1. scotch (recommended)
# 2. metis
# 3. hierarchical

# Check decomposition quality
decomposePar -celldist -decomposeParDict system/decomposeParDict.scotch
```

> 📂 **Source:** `.applications/utilities/parallelProcessing/decomposePar/decomposePar.C`

> **คำอธิบาย (Thai Explanation):**
> การวินิจฉัยและแก้ไขปัญหา decomposition:
> - **Load Balance Ratio**: อัตราส่วนของ cells สูงสุดต่อเฉลี่ย
> - **Method Comparison**: ทดลองใช้ methods ต่างกัน
> - **Visualization**: ใช้ -celldist เพื่อดู distribution
>
> **แนวคิดสำคัญ (Key Concepts):**
> 1. **Graph Partitioning**: แบ่ง graph เป็น subgraphs ที่ balance
> 2. **Edge Cuts**: ลด communication ระหว่าง subdomains
> 3. **Geometric vs Graph**: Geometric methods เร็วแต่ quality ต่ำ

---

## 6. Best Practices Summary

> [!TIP] **แนวทางปฏิบัติที่ดีที่สุด**

### 6.1 Solver Configuration
1. **Pressure Solver**: ใช้ GAMG สำหรับ pressure (multigrid)
2. **Velocity/Turbulence**: ใช้ smoothSolver หรือ PBiCGStab
3. **Tolerance**: `relTol = 0.01` สำหรับ intermediate, `0` สำหรับ final
4. **Preconditioning**: ใช้ DIC/DILU สำหรับ difficult cases

### 6.2 Decomposition
1. **Method**: ใช้ `scotch` สำหรับ complex geometry, `hierarchical` สำหรับ simple
2. **Load Balance**: ตรวจสอบ load balance ratio < 1.1
3. **Communication**: เลือก decomposition order เพื่อลด communication
4. **Verification**: ใช้ `-cellDist` เพื่อตรวจสอบ decomposition

### 6.3 I/O Optimization
1. **Compression**: เปิด `writeCompression on`
2. **Write Interval**: เพิ่มเพื่อลดความถี่การเขียน
3. **File System**: ใช้ parallel file system หากมี
4. **Collated I/O**: ใช้สำหรับ OpenFOAM v1806+

### 6.4 Memory Management
1. **Estimation**: คำนวณ memory requirement ล่วงหน้า
2. **Per Core**: ตรวจสอบ memory per core > 2GB
3. **Purge**: ใช้ `purgeWrite` เพื่อลบ old data
4. **Selective**: เลือกเขียนเฉพาะ fields ที่จำเป็น

### 6.5 Profiling
1. **Built-in**: ใช้ `libprofilingSo.so` สำหรับ basic profiling
2. **System Tools**: ใช้ `perf`, `vtune` สำหรับ detailed analysis
3. **MPI Tools**: ใช้ `mpiP`, `scalasca` สำหรับ MPI profiling
4. **Metrics**: ตรวจสอบ speedup และ parallel efficiency

### 6.6 Algorithmic Tuning
1. **Relaxation**: เริ่มจาก conservative values, ปรับตาม convergence
2. **Schemes**: ใช้ high-resolution schemes สำหรับ convection
3. **Non-orthogonal**: เพิ่ม nNonOrthogonalCorrectors สำหรับ bad mesh
4. **Time Step**: ปรับ deltaT ให้ Courant number < 1 (transient)

### 6.7 Workflow
1. **Incremental**: เริ่มจาก small cases ก่อน large cases
2. **Validation**: ตรวจสอบ results หลังจากแต่ละการเปลี่ยนแปลง
3. **Monitoring**: ใช้ real-time monitoring สำหรับ long runs
4. **Backup**: เก็บ backup ของ configurations ที่ใช้ได้

---

## 7. แหล่งอ้างอิงเพิ่มเติม

### 7.1 Internal Links
- `[[00_Overview#Parallel Computing Concepts]]`
- `[[01_Domain_Decomposition#Decomposition Methods]]`
- `[[02_Performance_Monitoring#Profiling Tools]]`

### 7.2 External Resources
- OpenFOAM User Guide: [Linear Solvers](https://www.openfoam.com/documentation/user-guide/)
- OpenFOAM Programmer's Guide: [Parallel Processing](https://www.openfoam.com/documentation/programmers-guide/)
- OpenFOAM Wiki: [Running in Parallel](https://openfoamwiki.net/index.php/Running_in_parallel)
- [GAMG Solver Documentation](https://www.openfoam.com/documentation/guide/)
- [Scotch Decomposition Manual](https://gforge.inria.fr/projects/scotch/)

### 7.3 Further Reading
- Ferziger, J.H., and Peric, M. (2002). *Computational Methods for Fluid Dynamics*. Springer.
- Hirsch, C. (2007). *Numerical Computation of Internal and External Flows*. Wiley.
- Saad, Y. (2003). *Iterative Methods for Sparse Linear Systems*. SIAM.

---

## 8. Performance Comparison Data

> [!INFO] **Performance Benchmarks**
> ข้อมูลต่อไปนี้เป็นตัวอย่าง performance benchmarks สำหรับ reference:
>
> ### 8.1 Solver Comparison (1M cells, 16 cores)
>
> | Solver | Setup | Solve | Total | Speedup |
> |--------|-------|-------|-------|---------|
> | simpleFoam (GAMG) | 2.3s | 145s | 147s | 12.1x |
> | simpleFoam (smoothSolver) | 2.3s | 387s | 389s | 4.6x |
>
> > **[MISSING DATA]**: Insert specific simulation results/graphs for your configuration
>
> ### 8.2 Decomposition Methods Comparison (4M cells, 32 cores)
>
> | Method | Load Balance | Comm. Time | Total Time |
> |--------|--------------|------------|------------|
> | scotch | 1.03 | 12.3s | 456s |
> | hierarchical | 1.12 | 15.7s | 482s |
> | simple | 1.34 | 23.1s | 521s |
>
> > **[MISSING DATA]**: Insert specific simulation results/graphs for your configuration
>
> ### 8.3 Scaling Analysis
>
> ```mermaid
> flowchart LR
>     A["1 Core: 1000s"] --> B["2 Cores: 520s"]
>     B --> C["4 Cores: 280s"]
>     C --> D["8 Cores: 150s"]
>     D --> E["16 Cores: 95s"]
>     E --> F["32 Cores: 65s"]
> ```
> > **Figure 3:** แผนภูมิแสดงตัวอย่างการวิเคราะห์การขยายตัว (Scaling Analysis) แสดงแนวโน้มของเวลาที่ใช้ในการคำนวณลดลงเมื่อเพิ่มจำนวนคอร์ประมวลผล ซึ่งใช้สำหรับการประเมินประสิทธิภาพและจุดคุ้มทุนในการใช้ทรัพยากรขนาน
>
> > **[MISSING DATA]**: Insert specific scaling results for your hardware and case
>
> ### 8.4 Memory Usage
>
> | Case Size | Cells/Core | Memory/Core | Total Memory |
> |-----------|------------|-------------|--------------|
> | Small (0.5M) | 31K | 250 MB | 4 GB |
> | Medium (2M) | 62K | 500 MB | 16 GB |
> | Large (10M) | 156K | 1.2 GB | 80 GB |
> | XLarge (50M) | 390K | 3.0 GB | 400 GB |
>
> > **[MISSING DATA]**: Insert specific memory measurements for your cases

---

## 9. Quick Reference Guide

### 9.1 Common Commands

```bash
# Decomposition
decomposePar                      # Standard decomposition
decomposePar -celldist            # With cell distribution
decomposePar -force               # Overwrite existing

# Parallel Execution
mpirun -np 4 <solver> -parallel   # OpenMPI
mpiexec -np 4 <solver> -parallel  # MPICH

# Reconstruction
reconstructPar                    # All time directories
reconstructPar -latestTime        # Latest time only
reconstructPar -newTimes          # Only non-existing

# Performance Monitoring
/usr/bin/time -v <command>        # Detailed timing
mpirun -np 4 -verbose <solver>    # Verbose output
```

### 9.2 Quick Troubleshooting

| Problem | Symptom | Solution |
|---------|---------|----------|
| Out of memory | "Killed" or segmentation fault | Reduce nProcs, enable compression |
| Slow convergence | Residuals plateau | Reduce relaxation, improve mesh |
| Poor scaling | Speedup < 0.5p | Check decomposition, I/O |
| Divergence | Residuals explode | Reduce deltaT, improve schemes |

---

**Document Version:** 1.0
**Last Updated:** 2025-12-24
**OpenFOAM Version:** 9+ (compatible with v2112+, v10+)
**Maintainer:** [Your Name]