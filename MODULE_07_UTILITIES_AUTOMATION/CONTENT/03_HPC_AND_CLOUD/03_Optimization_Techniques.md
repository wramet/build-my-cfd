# Optimization Techniques

เทคนิคการปรับแต่งประสิทธิภาพ

---

## 📚 Learning Objectives

** objectives การเรียนรู้**

After completing this section, you will be able to:

- **Identify** solver settings that impact parallel performance
- **Configure** I/O operations to minimize overhead
- **Optimize** memory usage for large-scale simulations
- **Select** appropriate numerical schemes for efficiency
- **Benchmark** and measure optimization effectiveness

**หลังจากจบส่วนนี้ คุณจะสามารถ:**

- ระบุการตั้งค่า solver ที่มีผลต่อประสิทธิภาพการทำงานแบบ parallel
- กำหนดค่าการทำงาน I/O เพื่อลดความซับซ้อน
- ปรับแต่งการใช้หน่วยความจำสำหรับการจำลองขนาดใหญ่
- เลือก scheme ทางคณิตศาสตร์ที่เหมาะสมเพื่อประสิทธิภาพ
- วัดและประเมินผลการปรับแต่ง

**Estimated Completion Time:** 45-60 minutes  
**Difficulty Level:** ⚫⚫⚪⚪⚪ Intermediate

---

## 📋 Prerequisites

**ข้อกำหนดเบื้องต้น**

Before starting this section, ensure you have:

- Completed [01_Domain_Decomposition.md](01_Domain_Decomposition.md) ✓
- Completed [02_Performance_Monitoring.md](02_Performance_Monitoring.md) ✓
- Understanding of OpenFOAM solver syntax
- Experience running basic parallel simulations
- Familiarity with OpenFOAM dictionary structure

**ก่อนเริ่มส่วนนี้ ให้แน่ใจว่าคุณ:**

- ศึกษา 01_Domain_Decomposition.md แล้ว
- ศึกษา 02_Performance_Monitoring.md แล้ว
- เข้าใจ syntax ของ OpenFOAM solver
- มีประสบการณ์การรัน parallel simulation พื้นฐาน
- คุ้นเคยกับโครงสร้าง dictionary ใน OpenFOAM

---

## 🎯 Core Content: Optimization Techniques

**เนื้อหาหลัก: เทคนิคการปรับแต่งประสิทธิภาพ**

---

### 1. I/O Optimization

**การปรับแต่งประสิทธิภาพ I/O**

#### WHAT (คืออะไร)

I/O operations (reading/writing files) are often the **bottleneck** in parallel CFD simulations. OpenFOAM writes:
- Field data (pressure, velocity, etc.)
- Geometry/mesh information
- Residuals and convergence data
- Execution time logs

การกระทำ I/O (การอ่าน/เขียนไฟล์) มักเป็น **คอขวด** ในการจำลอง CFD แบบ parallel OpenFOAM เขียน:
- ข้อมูล field (ความดัน, ความเร็ว, ฯลฯ)
- ข้อมูลเรขาคณิต/เมช
- ข้อมูล residuals และการลู่เข้า
- บันทึกเวลาการทำงาน

#### WHY (ทำไมสำคัญ)

**Performance Impact:**
- I/O can consume **30-50%** of total simulation time
- Network storage (NFS/Lustre) exacerbates the problem
- Every processor writes simultaneously → I/O contention
- Large datasets take longer to write, even with compression

**ผลต่อประสิทธิภาพ:**
- I/O สามารถใช้เวลาถึง **30-50%** ของเวลาจำลองทั้งหมด
- ที่เก็บข้อมูลแบบ network (NFS/Lustre) ทำให้ปัญหาแย่ลง
- ทุก processor เขียนพร้อมกัน → การแย่งชิง I/O
- ชุดข้อมูลขนาดใหญ่ใช้เวลานานขึ้นในการเขียน แม้มีการบีบอัด

#### HOW (วิธีการ)

**Step 1: Reduce Write Frequency**

```cpp
// system/controlDict
// WHAT: Control when data is written
// WHY: Fewer writes = less I/O overhead
// HOW: Choose appropriate writeControl and writeInterval

// Option A: Write at fixed time intervals (most common)
writeControl    runTime;
writeInterval   0.5;  // Write every 0.5 seconds

// Option B: Write at fixed timestep intervals
writeControl    timeStep;
writeInterval   100;  // Write every 100 timesteps

// Option C: Write at adjustable runtime (recommended for long simulations)
writeControl    adjustableRunTime;
writeInterval   1.0;  // Target: write every 1.0s (adjusted automatically)
```

**Step 1: ลดความถี่ในการเขียน**

```cpp
// system/controlDict
// คืออะไร: ควบคุมเวลาที่ข้อมูลจะถูกเขียน
// ทำไม: เขียนน้อยลง = ค่าใช้จ่าย I/O น้อยลง
// วิธีการ: เลือก writeControl และ writeInterval ที่เหมาะสม

// ตัวเลือก A: เขียนตามช่วงเวลาคงที่ (พบบ่อยที่สุด)
writeControl    runTime;
writeInterval   0.5;  // เขียนทุก 0.5 วินาที

// ตัวเลือก B: เขียนตามช่วง timestep คงที่
writeControl    timeStep;
writeInterval   100;  // เขียนทุก 100 timesteps

// ตัวเลือก C: เขียนตาม runtime ที่ปรับได้ (แนะนำสำหรับการจำลองยาว)
writeControl    adjustableRunTime;
writeInterval   1.0;  // เป้าหมาย: เขียนทุก 1.0 วินาที (ปรับอัตโนมัติ)
```

**Step 2: Compress Output Files**

```cpp
// system/controlDict
// WHAT: Compress written files to reduce storage and I/O
// WHY: Smaller files = faster writes, less disk space
// HOW: Enable writeCompression

writeCompression compressed;

// Alternative: uncompressed (for debugging, faster writes on slow CPUs)
writeCompression uncompressed;

// Alternative: off (no compression, fastest I/O, most space)
writeCompression off;
```

**Step 2: บีบอัดไฟล์ Output**

```cpp
// system/controlDict
// คืออะไร: บีบอัดไฟล์ที่เขียนเพื่อลดพื้นที่และ I/O
// ทำไม: ไฟล์เล็กลง = เขียนเร็วขึ้น, ใช้ดิสก์น้อยลง
// วิธีการ: เปิด writeCompression

writeCompression compressed;

// ทางเลือก: uncompressed (สำหรับ debugging, เขียนเร็วขึ้นบน CPU ช้า)
writeCompression uncompressed;

// ทางเลือก: off (ไม่บีบอัด, I/O เร็วที่สุด, ใช้พื้นที่มากที่สุด)
writeCompression off;
```

**Step 3: Optimize What Gets Written**

```cpp
// system/controlDict
// WHAT: Control which fields are written
// WHY: Writing unnecessary fields wastes I/O bandwidth
// HOW: Customize fields list

// Example: Write only essential fields for post-processing
functions
{
    // Write only specific fields
    writeCellCentres
    {
        type            cellSource;
        functionObject  libsampling.so;
        // ... configuration
    }
}
```

**Step 3: ปรับแต่งสิ่งที่เขียน**

```cpp
// system/controlDict
// คืออะไร: ควบคุมว่า field ใดจะถูกเขียน
// ทำไม: การเขียน field ที่ไม่จำเป็น ทิ้งขวาง I/O bandwidth
// วิธีการ: ปรับแต่งรายการ fields

// ตัวอย่าง: เขียนเฉพาะ field ที่จำเป็นสำหรับ post-processing
functions
{
    // เขียนเฉพาะ field เฉพาะ
    writeCellCentres
    {
        type            cellSource;
        functionObject  libsampling.so;
        // ... configuration
    }
}
```

---

### 2. Solver Settings Optimization

**การปรับแต่งค่า Solver**

#### WHAT (คืออะไร)

OpenFOAM provides **multiple solver algorithms** and **preconditioners** to solve linear systems (pressure, velocity, etc.). The choice significantly impacts:
- Convergence rate (how fast solution is found)
- Computational cost per iteration
- Parallel scalability

OpenFOAM มอบ **อัลกอริทึม solver หลายแบบ** และ **preconditioner** เพื่อแก้ระบบเชิงเส้น (ความดัน, ความเร็ว, ฯลฯ) การเลือกมีผลกระทบอย่างมาก:
- อัตราการลู่เข้า (ความเร็วในการหาคำตอบ)
- ต้นทุนการคำนวณต่อ iteration
- ความสามารถขยายแบบ parallel

#### WHY (ทำไมสำคัญ)

**Performance Gains:**
- Good preconditioner can reduce iterations by **50-80%**
- Proper tolerance settings prevent over/under-solving
- Solver choice affects parallel communication patterns
- Can reduce total simulation time by **20-40%**

**ผลประโยชน์ด้านประสิทธิภาพ:**
- Preconditioner ที่ดีสามารถลด iterations ลง **50-80%**
- การตั้งค่า tolerance ที่เหมาะสมป้องกันการแก้เกิน/ไม่เพียงพอ
- ตัวเลือก solver มีผลต่อรูปแบบการสื่อสาร parallel
- สามารถลดเวลาจำลองทั้งหมดลง **20-40%**

#### HOW (วิธีการ)

**Step 1: Select Appropriate Solver**

```cpp
// system/fvSolution
// WHAT: Choose linear system solver
// WHY: Different solvers excel for different matrix types
// HOW: Match solver to physics and matrix properties

// For symmetric matrices (pressure in incompressible flows)
solvers
{
    p
    {
        solver          PCG;  // Preconditioned Conjugate Gradient
        preconditioner  DIC;  // Diagonal Incomplete Cholesky
        tolerance       1e-06;
        relTol          0.1;
    }
}

// For asymmetric matrices (velocity, compressible flows)
solvers
{
    U
    {
        solver          PBiCGStab;  // Stabilized Bi-Conjugate Gradient
        preconditioner  DILU;       // Diagonal Incomplete LU
        tolerance       1e-05;
        relTol          0.1;
    }
}
```

**Step 1: เลือก Solver ที่เหมาะสม**

```cpp
// system/fvSolution
// คืออะไร: เลือก solver ระบบเชิงเส้น
// ทำไม: solver ที่แตกต่างเหมาะกับเมทริกซ์ที่แตกต่างกัน
// วิธีการ: จับคู่ solver กับฟิสิกส์และคุณสมบัติเมทริกซ์

// สำหรับเมทริกซ์สมมาตร (ความดันในการไหลแบบอัดไม่ได้)
solvers
{
    p
    {
        solver          PCG;  // Preconditioned Conjugate Gradient
        preconditioner  DIC;  // Diagonal Incomplete Cholesky
        tolerance       1e-06;
        relTol          0.1;
    }
}

// สำหรับเมทริกซ์ไม่สมมาตร (ความเร็ว, การไหลแบบอัดได้)
solvers
{
    U
    {
        solver          PBiCGStab;  // Stabilized Bi-Conjugate Gradient
        preconditioner  DILU;       // Diagonal Incomplete LU
        tolerance       1e-05;
        relTol          0.1;
    }
}
```

**Step 2: Set Appropriate Tolerances**

```cpp
// WHAT: Control solver convergence criteria
// WHY: Too tight = wasted iterations, too loose = inaccurate solution
// HOW: Balance absolute (tolerance) and relative (relTol) tolerances

solvers
{
    p
    {
        solver          PCG;
        preconditioner  DIC;
        
        // Absolute tolerance: stop when residual < 1e-06
        tolerance       1e-06;
        
        // Relative tolerance: stop when residual reduced by factor of relTol
        relTol          0.1;  // Stop when residual is 10% of initial
        
        // Recommended settings:
        // - For pressure: tolerance 1e-06 to 1e-07, relTol 0.01 to 0.1
        // - For velocity: tolerance 1e-05 to 1e-06, relTol 0.05 to 0.1
    }
}
```

**Step 2: ตั้งค่า Tolerance ที่เหมาะสม**

```cpp
// คืออะไร: ควบคุมเกณฑ์การลู่เข้าของ solver
// ทำไม: แน่นเกินไป = iteration สิ้นเปลือง, หลวมเกินไป = คำตอบไม่แม่นยำ
// วิธีการ: สมดุล tolerance สัมบูรณ์ (tolerance) และสัมพัทธ์ (relTol)

solvers
{
    p
    {
        solver          PCG;
        preconditioner  DIC;
        
        // Absolute tolerance: หยุดเมื่อ residual < 1e-06
        tolerance       1e-06;
        
        // Relative tolerance: หยุดเมื่อ residual ลดลงตาม factor ของ relTol
        relTol          0.1;  // หยุดเมื่อ residual เป็น 10% ของค่าเริ่มต้น
        
        // การตั้งค่าที่แนะนำ:
        // - สำหรับความดัน: tolerance 1e-06 ถึง 1e-07, relTol 0.01 ถึง 0.1
        // - สำหรับความเร็ว: tolerance 1e-05 ถึง 1e-06, relTol 0.05 ถึง 0.1
    }
}
```

**Step 3: Advanced Preconditioners (for Large Cases)**

```cpp
// WHAT: Use more sophisticated preconditioners for better convergence
// WHY: Better preconditioning = fewer iterations, but more cost per iteration
// HOW: Choose based on problem size and available memory

solvers
{
    p
    {
        solver          PCG;
        
        // GAMG: Geometric-Algebraic Multi-Grid (excellent for large cases)
        preconditioner  GAMG;
        tolerance       1e-06;
        relTol          0.1;
        
        smoother        DIC;  // Smoother for GAMG
        
        // GAMG parameters
        nCellsInCoarsestLevel 10;  // Min cells in coarsest level
        mergeLevels             1;  // Level merging strategy
    }
}

// Note: GAMG is especially effective for:
// - Large meshes (> 1M cells)
// - Pressure equations in incompressible flows
// - Problems with smooth solutions
```

**Step 3: Preconditioners ขั้นสูง (สำหรับกรณีขนาดใหญ่)**

```cpp
// คืออะไร: ใช้ preconditioner ที่ซับซ้อนมากขึ้นสำหรับการลู่เข้าที่ดีขึ้น
// ทำไม: preconditioning ที่ดีขึ้น = iteration น้อยลง แต่ต้นทุนต่อ iteration สูงขึ้น
// วิธีการ: เลือกตามขนาดปัญหาและหน่วยความจำที่มี

solvers
{
    p
    {
        solver          PCG;
        
        // GAMG: Geometric-Algebraic Multi-Grid (ยอดเยี่ยมสำหรับกรณีใหญ่)
        preconditioner  GAMG;
        tolerance       1e-06;
        relTol          0.1;
        
        smoother        DIC;  // Smoother สำหรับ GAMG
        
        // พารามิเตอร์ GAMG
        nCellsInCoarsestLevel 10;  // เซลล์น้อยที่สุดในระดับหยาบที่สุด
        mergeLevels             1;  // กลยุทธ์การรวมระดับ
    }
}

// หมายเหตุ: GAMG มีประสิทธิภาพเป็นพิเศษสำหรับ:
// - เมชขนาดใหญ่ (> 1M เซลล์)
// - สมการความดันในการไหลแบบอัดไม่ได้
// - ปัญหาที่มีคำตอบเรียบ
```

---

### 3. Memory Optimization

**การปรับแต่งหน่วยความจำ**

#### WHAT (คืออะไร)

Memory usage in OpenFOAM includes:
- **Field storage** (pressure, velocity, temperature, etc.)
- **Matrix storage** (linear system coefficients)
- **Decomposition data** (processor boundaries, halo cells)
- **Temporary variables** during computation

การใช้หน่วยความจำใน OpenFOAM ประกอบด้วย:
- **การเก็บ field** (ความดัน, ความเร็ว, อุณหภูมิ, ฯลฯ)
- **การเก็บเมทริกซ์** (สัมประสิทธิ์ระบบเชิงเส้น)
- **ข้อมูลการแยก** (ขอบเขต processor, เซลล์ halo)
- **ตัวแปรชั่วคราว** ระหว่างการคำนวณ

#### WHY (ทำไมสำคัญ)

**Memory Constraints:**
- Each processor has **limited RAM** (typically 64-256 GB on HPC)
- Exceeding memory causes **out-of-memory errors** or **swapping** (slow!)
- More memory usage = **fewer cores per node** = inefficient resource use
- Memory bandwidth is often the **performance bottleneck**

**ข้อจำกัดหน่วยความจำ:**
- แต่ละ processor มี **RAM จำกัด** (โดยทั่วไป 64-256 GB บน HPC)
- เกินหน่วยความจำทำให้เกิด **out-of-memory errors** หรือ **swapping** (ช้า!)
- ใช้หน่วยความจำมากขึ้น = **core น้อยลงต่อโหนด** = ใช้ทรัพยากรไม่มีประสิทธิภาพ
- แบนด์วิดท์หน่วยความจำมักเป็น **คอขวดประสิทธิภาพ**

#### HOW (วิธีการ)

**Step 1: Monitor Memory Usage**

```bash
# WHAT: Check real-time memory consumption
# WHY: Identify memory leaks or excessive usage
# HOW: Use system tools or OpenFOAM utilities

# Method 1: Check during simulation
/usr/bin/time -v mpirun -np 4 solver -parallel 2>&1 | grep "Maximum resident"

# Method 2: Monitor with top (process ID)
top -p <PID>

# Method 3: Check per-processor memory
foamListTimes
grep 'ExecutionTime' log.* | tail -1
```

**Step 1: ตรวจสอบการใช้หน่วยความจำ**

```bash
# คืออะไร: ตรวจสอบการใช้หน่วยความจำแบบ real-time
# ทำไม: ระบุ memory leaks หรือการใช้งานมากเกินไป
# วิธีการ: ใช้เครื่องมือระบบหรือ utilities ของ OpenFOAM

# วิธี 1: ตรวจสอบระหว่างการจำลอง
/usr/bin/time -v mpirun -np 4 solver -parallel 2>&1 | grep "Maximum resident"

# วิธี 2: ตรวจสอบด้วย top (process ID)
top -p <PID>

# วิธี 3: ตรวจสอบหน่วยความจำต่อ processor
foamListTimes
grep 'ExecutionTime' log.* | tail -1
```

**Step 2: Reduce Field Storage**

```cpp
// system/controlDict
// WHAT: Minimize number of stored fields
// WHY: Each field = significant memory overhead
// HOW: Write only essential fields

// Bad: Store everything (memory intensive)
writeControl    runTime;
writeInterval   0.1;

// Good: Write less frequently
writeControl    runTime;
writeInterval   0.5;  // 5x less I/O and storage

// Advanced: Selective field writing
functions
{
    // Write only required fields for post-processing
    surfaces
    {
        type            surfaces;
        surfaceFormat   vtk;
        fields          (p U);  // Only p and U
    }
}
```

**Step 2: ลดการเก็บ Field**

```cpp
// system/controlDict
// คืออะไร: ลดจำนวน field ที่เก็บ
// ทำไม: แต่ละ field = ค่าใช้จ่ายหน่วยความจำสำคัญ
// วิธีการ: เขียนเฉพาะ field ที่จำเป็น

// ไม่ดี: เก็บทุกอย่าง (ใช้หน่วยความจำมาก)
writeControl    runTime;
writeInterval   0.1;

// ดี: เขียนน้อยลง
writeControl    runTime;
writeInterval   0.5;  // I/O และพื้นที่น้อยลง 5 เท่า

// ขั้นสูง: การเขียน field แบบเลือก
functions
{
    // เขียนเฉพาะ field ที่ต้องการสำหรับ post-processing
    surfaces
    {
        type            surfaces;
        surfaceFormat   vtk;
        fields          (p U);  // เฉพาะ p และ U
    }
}
```

**Step 3: Optimize Decomposition for Memory**

```bash
# WHAT: Balance memory usage across processors
# WHY: Prevent single processor from exceeding memory limit
# HOW: Choose decomposition method carefully

# Use scotch for automatic load AND memory balancing
method scotch;

# For manual decomposition, ensure balanced cell counts
method simple;
simpleCoeffs
{
    n (4 2 1);  // 8 processors
}

# Check memory balance after decomposition
ls -lrth processor*
du -sh processor*  # Check disk usage (proxy for memory)
```

**Step 3: ปรับแต่งการแยกเพื่อหน่วยความจำ**

```bash
# คืออะไร: สมดุลการใช้หน่วยความจำข้าม processor
# ทำไม: ป้องกัน processor เดียวเกินขีดจำกัดหน่วยความจำ
# วิธีการ: เลือกวิธีการแยกอย่างระมัดระวัง

# ใช้ scotch สำหรับการสมดุลโหลดและหน่วยความจำอัตโนมัติ
method scotch;

# สำหรับการแยกแบบ manual ให้แน่ใจว่า cell count สมดุล
method simple;
simpleCoeffs
{
    n (4 2 1);  // 8 processors
}

# ตรวจสอบความสมดุลหน่วยความจำหลังการแยก
ls -lrth processor*
du -sh processor*  # ตรวจสอบการใช้ดิสก์ (proxy สำหรับหน่วยความจำ)
```

---

### 4. Numerical Scheme Tuning

**การปรับแต่ง Scheme ทางคณิตศาสตร์**

#### WHAT (คืออะไร)

**Numerical schemes** determine how OpenFOAM discretizes (converts to algebra) the governing equations:
- **Time integration schemes** (Euler, Crank-Nicolson, etc.)
- **Gradient schemes** (Gauss linear, leastSquares, etc.)
- **Divergence schemes** (upwind, linear, TVD, etc.)
- **Laplacian schemes** (Gauss linear corrected, etc.)

**Scheme ทางคณิตศาสตร์** กำหนดวิธีที่ OpenFOAM discretize (แปลงเป็นพีชคณิต) สมการควบคุม:
- **Scheme การผสานเวลา** (Euler, Crank-Nicolson, ฯลฯ)
- **Scheme การไล่ระดับ** (Gauss linear, leastSquares, ฯลฯ)
- **Scheme การเบี่ยงเบน** (upwind, linear, TVD, ฯลฯ)
- **Scheme ลาปลาซ** (Gauss linear corrected, ฯลฯ)

#### WHY (ทำไมสำคัญ)

**Performance vs. Accuracy Trade-off:**
- **Higher-order schemes** = more accurate but more expensive computationally
- **Lower-order schemes** = faster but may introduce numerical diffusion
- Proper scheme selection can reduce **iterations by 20-50%**
- Affects matrix conditioning and solver convergence

**การแลกเปลี่ยนประสิทธิภาพกับความแม่นยำ:**
- **Scheme ลำดับสูง** = แม่นยำกว่าแต่คำนวณแพงกว่า
- **Scheme ลำดับต่ำ** = เร็วกว่าแต่อาจแนะนำการกระจายตัวเชิงคณิตศาสตร์
- การเลือก scheme ที่เหมาะสมสามารถลด **iterations ลง 20-50%**
- มีผลต่อ conditioning เมทริกซ์และการลู่เข้าของ solver

#### HOW (วิธีการ)

**Step 1: Time Integration Schemes**

```cpp
// system/fvSchemes
// WHAT: Choose temporal discretization scheme
// WHY: Affects stability, accuracy, and computational cost
// HOW: Balance stability (CFL) with computational efficiency

ddtSchemes
{
    // Option A: Euler (first-order, very stable, fast)
    default         Euler;
    
    // Option B: Backward (second-order, more stable than Crank-Nicolson)
    default         backward;
    
    // Option C: Crank-Nicolson (second-order, accurate, but less stable)
    default         CrankNicolson 0.5;  // 0.5 = blend factor (0.5 = CN, 1.0 = backward)
    
    // Option D: Local Euler (for steady-state or pseudo-transient)
    default         localEuler;
}

// Recommendation:
// - Start with Euler or backward for stability
// - Use Crank-Nicolson for accuracy (if stable)
// - For transient flows: maxCo < 1.0 for explicit, can use larger for implicit
```

**Step 1: Scheme การผสานเวลา**

```cpp
// system/fvSchemes
// คืออะไร: เลือก scheme การ discretization เชิงเวลา
// ทำไม: ส่งผลต่อเสถียรภาพ ความแม่นยำ และต้นทุนการคำนวณ
// วิธีการ: สมดุลเสถียรภาพ (CFL) กับประสิทธิภาพการคำนวณ

ddtSchemes
{
    // ตัวเลือก A: Euler (ลำดับหนึ่ง, เสถียรมาก, เร็ว)
    default         Euler;
    
    // ตัวเลือก B: Backward (ลำดับสอง, เสถียรกว่า Crank-Nicolson)
    default         backward;
    
    // ตัวเลือก C: Crank-Nicolson (ลำดับสอง, แม่นยำ, แต่เสถียรน้อยกว่า)
    default         CrankNicolson 0.5;  // 0.5 = ปัจจัยผสม (0.5 = CN, 1.0 = backward)
    
    // ตัวเลือก D: Local Euler (สำหรับ steady-state หรือ pseudo-transient)
    default         localEuler;
}

// คำแนะนำ:
// - เริ่มต้นด้วย Euler หรือ backward สำหรับเสถียรภาพ
// - ใช้ Crank-Nicolson สำหรับความแม่นยำ (ถ้าเสถียร)
// - สำหรับการไหล transient: maxCo < 1.0 สำหรับ explicit, สามารถใช้ใหญ่กว่าสำหรับ implicit
```

**Step 2: Gradient Schemes**

```cpp
// system/fvSchemes
// WHAT: Compute cell-centered gradients (used in many terms)
// WHY: Affects accuracy of diffusion, pressure gradient, etc.
// HOW: Choose based on mesh quality and accuracy requirements

gradSchemes
{
    // Option A: Gauss linear (standard, second-order on orthogonal meshes)
    default         Gauss linear;
    
    // Option B: Gauss linear corrected (better on non-orthogonal meshes)
    default         Gauss linear corrected;
    
    // Option C: leastSquares (more accurate on highly skewed meshes, expensive)
    default         leastSquares;
    
    // Option D: fourth (fourth-order, very accurate, very expensive)
    default         fourth;
}

// Recommendation:
// - Use Gauss linear for good quality meshes
// - Use Gauss linear corrected for non-orthogonal meshes (most common)
// - Use leastSquares only for highly skewed meshes (last resort)
```

**Step 2: Scheme การไล่ระดับ**

```cpp
// system/fvSchemes
// คืออะไร: คำนวณการไล่ระดับที่จุดศูนย์กลางเซลล์ (ใช้ในหลายพจน์)
// ทำไม: ส่งผลต่อความแม่นยำของการกระจาย การไล่ระดับความดัน ฯลฯ
// วิธีการ: เลือกตามคุณภาพเมชและความต้องการความแม่นยำ

gradSchemes
{
    // ตัวเลือก A: Gauss linear (มาตรฐาน, ลำดับสองบนเมชตั้งฉาก)
    default         Gauss linear;
    
    // ตัวเลือก B: Gauss linear corrected (ดีกว่าบนเมชไม่ตั้งฉาก)
    default         Gauss linear corrected;
    
    // ตัวเลือก C: leastSquares (แม่นยำกว่าบนเมชบิดเบี้ยวมาก, แพง)
    default         leastSquares;
    
    // ตัวเลือก D: fourth (ลำดับสี่, แม่นยำมาก, แพงมาก)
    default         fourth;
}

// คำแนะนำ:
// - ใช้ Gauss linear สำหรับเมชคุณภาพดี
// - ใช้ Gauss linear corrected สำหรับเมชไม่ตั้งฉาก (พบบ่อยที่สุด)
// - ใช้ leastSquares เฉพาะกรณีเมชบิดเบี้ยวมาก (ทางเลือกสุดท้าย)
```

**Step 3: Divergence Schemes (Convection Terms)**

```cpp
// system/fvSchemes
// WHAT: Discretize convection terms (∇·(φU))
// WHY: Most important for stability and accuracy in convective flows
// HOW: Balance numerical stability with accuracy

divSchemes
{
    // Option A: Upwind (first-order, very stable, numerical diffusion)
    default         Gauss upwind;
    
    // Option B: Linear (second-order, accurate, but may oscillate)
    default         Gauss linear;
    
    // Option C: LimitedLinear (second-order, bounded, good compromise)
    default         Gauss limitedLinear 1;  // 1 = limiting (0=upwind, 1=fully limited)
    
    // Option D: TVD schemes (e.g., van Leer, SUPERBEE, etc.)
    default         Gauss vanLeer;
    default         Gauss SUPERBEE;
    
    // Recommended: Use limited schemes for stability + accuracy
    div(phi,U)      Gauss limitedLinearV 1;  // For velocity
    div(phi,k)      Gauss limitedLinearV 1;  // For turbulence k
    div(phi,epsilon) Gauss limitedLinearV 1;  // For turbulence epsilon
}

// Recommendation:
// - Start with upwind for stability (debugging)
// - Use limitedLinear or vanLeer for production runs (good balance)
// - Avoid pure linear (unbounded, may crash)
```

**Step 3: Scheme การเบี่ยงเบน (Convection Terms)**

```cpp
// system/fvSchemes
// คืออะไร: Discretize พจน์ convection (∇·(φU))
// ทำไม: สำคัญที่สุดสำหรับเสถียรภาพและความแม่นยำในการไหลแบบ convection
// วิธีการ: สมดุลเสถียรภาพเชิงคณิตศาสตร์กับความแม่นยำ

divSchemes
{
    // ตัวเลือก A: Upwind (ลำดับหนึ่ง, เสถียรมาก, การกระจายตัวเชิงคณิตศาสตร์)
    default         Gauss upwind;
    
    // ตัวเลือก B: Linear (ลำดับสอง, แม่นยำ, แต่อาจสั่น)
    default         Gauss linear;
    
    // ตัวเลือก C: LimitedLinear (ลำดับสอง, จำกัด, คอมโพรไมส์ดี)
    default         Gauss limitedLinear 1;  // 1 = การจำกัด (0=upwind, 1=จำกัดเต็ม)
    
    // ตัวเลือก D: Scheme TVD (เช่น van Leer, SUPERBEE, ฯลฯ)
    default         Gauss vanLeer;
    default         Gauss SUPERBEE;
    
    // แนะนำ: ใช้ scheme ที่จำกัดสำหรับเสถียรภาพ + ความแม่นยำ
    div(phi,U)      Gauss limitedLinearV 1;  // สำหรับความเร็ว
    div(phi,k)      Gauss limitedLinearV 1;  // สำหรับ k ความปั่น
    div(phi,epsilon) Gauss limitedLinearV 1;  // สำหรับ epsilon ความปั่น
}

// คำแนะนำ:
// - เริ่มต้นด้วย upwind สำหรับเสถียรภาพ (debugging)
// - ใช้ limitedLinear หรือ vanLeer สำหรับการรันการผลิต (สมดุลดี)
// - หลีกเลี่ยง linear บริสุทธิ์ (ไม่จำกัด, อาจขัดข้อง)
```

---

## 🌳 Optimization Workflow: Decision Tree

**เวิร์กโฟลว์การปรับแต่ง: ต้นไม้การตัดสินใจ**

```
START
  │
  ├─→ Is simulation I/O bound?
  │   ├─→ YES: Reduce write frequency (writeInterval)
  │   ├─→ YES: Enable compression (writeCompression)
  │   └─→ YES: Selective field writing
  │
  ├─→ Is simulation solver bound (slow convergence)?
  │   ├─→ YES: Check preconditioner (try GAMG for pressure)
  │   ├─→ YES: Verify tolerances (not too tight/loose)
  │   └─→ YES: Consider solver type (PCG vs PBiCGStab)
  │
  ├─→ Is simulation memory bound?
  │   ├─→ YES: Reduce stored fields (writeInterval)
  │   ├─→ YES: Re-decompose with better balance (scotch)
  │   └─→ YES: Reduce mesh resolution or use coarser levels
  │
  └─→ Is simulation unstable?
      ├─→ YES: Use more stable schemes (upwind, Euler)
      ├─→ YES: Reduce timestep (maxCo < 1.0)
      └─→ YES: Check mesh quality (non-orthogonality)
```

---

## 🧪 Benchmarking Methodology

**วิธีการ Benchmarking**

### 1. Establish Baseline Performance

**สร้างประสิทธิภาพพื้นฐาน**

```bash
# WHAT: Measure current performance before optimization
# WHY: Quantify improvements and identify bottlenecks
# HOW: Run short test case with timing enabled

# Run baseline simulation
mpirun -np 4 solver -parallel > log.baseline 2>&1

# Extract key metrics
grep "ExecutionTime" log.baseline | tail -1
grep "Courant Number" log.baseline | tail -5

# Check solver iterations
grep "solver p:" log.baseline | tail -10
```

### 2. Test Individual Optimizations

**ทดสอบการปรับแต่งแต่ละรายการ**

```bash
# WHAT: Change one setting at a time
# WHY: Isolate effect of each optimization
# HOW: Keep all else constant, vary one parameter

# Test A: Different write intervals
# Edit writeInterval: 0.1 → 0.5 → 1.0
mpirun -np 4 solver -parallel > log.testA 2>&1

# Test B: Different solvers
# Edit preconditioner: DIC → GAMG
mpirun -np 4 solver -parallel > log.testB 2>&1

# Test C: Different schemes
# Edit divSchemes: upwind → limitedLinear
mpirun -np 4 solver -parallel > log.testC 2>&1

# Compare results
echo "Baseline:" $(grep "ExecutionTime" log.baseline | tail -1 | awk '{print $3}')
echo "Test A:" $(grep "ExecutionTime" log.testA | tail -1 | awk '{print $3}')
echo "Test B:" $(grep "ExecutionTime" log.testB | tail -1 | awk '{print $3}')
```

### 3. Measure Speedup and Efficiency

**วัดความเร็วและประสิทธิภาพ**

```bash
# WHAT: Quantify performance improvement
# WHY: Validate optimization effectiveness
# HOW: Calculate speedup ratio and percentage improvement

# Speedup = Baseline Time / Optimized Time
baseline_time=$(grep "ExecutionTime" log.baseline | tail -1 | awk '{print $3}')
optimized_time=$(grep "ExecutionTime" log.optimized | tail -1 | awk '{print $3}')
speedup=$(echo "$baseline_time / $optimized_time" | bc -l)

echo "Speedup: $speedup"
echo "Improvement: $(echo "($baseline_time - $optimized_time) / $baseline_time * 100" | bc -l)%"

# Target: > 20% improvement for significant optimization
```

---

## 🔍 Practical Examples

**ตัวอย่างปฏิบัติ**

### Example 1: Optimizing Large Transient Case

**ตัวอย่าง 1: การปรับแต่งกรณี Transient ขนาดใหญ่**

**Scenario:** 10M cell mesh, transient simulation, I/O bottlenecks  
**กรณี:** เมช 10M เซลล์, การจำลอง transient, คอขวด I/O

```cpp
// === BEFORE (Slow) ===
// system/controlDict
writeControl    runTime;
writeInterval   0.05;  // Writing too frequently
writeCompression off;

// === AFTER (Optimized) ===
// system/controlDict
writeControl    adjustableRunTime;  // Smart write timing
writeInterval   0.5;  // 10x less I/O
writeCompression compressed;  // Reduce storage

// system/fvSolution
solvers
{
    p
    {
        solver          PCG;
        preconditioner  GAMG;  // Faster convergence
        tolerance       1e-06;
        relTol          0.05;  // Slightly relaxed
        smoother        DIC;
    }
}

// Result: 3.2x speedup (128 hours → 40 hours)
```

### Example 2: Memory-Constrained Simulation

**ตัวอย่าง 2: การจำลองที่มีข้อจำกัดหน่วยความจำ**

**Scenario:** 50M cell mesh, limited RAM (128 GB per node)  
**กรณี:** เมช 50M เซลล์, RAM จำกัด (128 GB ต่อโหนด)

```bash
# Problem: Out-of-memory errors with 32 cores per node
# Solution: Reduce memory usage

# Step 1: Re-decompose with fewer cells per processor
decomposePar

# Step 2: Selective field writing
# system/controlDict
writeControl    runTime;
writeInterval   1.0;  // Less frequent
writeCompression compressed;

# Step 3: Use memory-efficient solver
# system/fvSolution
solvers
{
    p
    {
        solver          PCG;
        preconditioner  DIC;  // Less memory than GAMG
    }
}

# Result: Successful run (no OOM errors), 15% slower but works
```

---

## 🚨 Troubleshooting

**การแก้ปัญหา**

### Issue 1: Simulation Slower After Optimization

**ปัญหา 1: การจำลองช้าลงหลังการปรับแต่ง**

**Symptoms:**
- Execution time increased after changing settings
- More iterations per timestep

**อาการ:**
- เวลาการทำงานเพิ่มขึ้นหลังเปลี่ยนการตั้งค่า
- Iteration มากขึ้นต่อ timestep

**Solutions:**

1. **Check tolerance settings**
   ```cpp
   // Too tight: wasting iterations
   tolerance       1e-08;  // BAD
   
   // Better: realistic tolerance
   tolerance       1e-06;  // GOOD
   ```

2. **Verify preconditioner choice**
   ```cpp
   // GAMG may be slower for small cases
   // Use DIC for < 1M cells
   
   preconditioner  DIC;  // Better for small cases
   ```

3. **Test scheme stability**
   ```cpp
   // Limited schemes add overhead
   // Use upwind for debugging
   
   divSchemes
   {
       default         Gauss upwind;  // Fast but diffusive
   }
   ```

**การแก้:**

1. **ตรวจสอบการตั้งค่า tolerance**
2. **ตรวจสอบตัวเลือก preconditioner**
3. **ทดสอบเสถียรภาพ scheme**

---

### Issue 2: Solution Diverges After Optimization

**ปัญหา 2: คำตอบ Diverge หลังการปรับแต่ง**

**Symptoms:**
- Residuals increasing
- Simulation crashes
- "Maximum number of iterations" errors

**อาการ:**
- Residuals เพิ่มขึ้น
- การจำลองขัดข้อง
- ข้อผิดพลาด "Maximum number of iterations"

**Solutions:**

1. **Reduce timestep**
   ```cpp
   // system/controlDict
   maxCo           0.5;  // Was 1.0, reduce for stability
   ```

2. **Use more stable schemes**
   ```cpp
   // system/fvSchemes
   divSchemes
   {
       default         Gauss upwind;  // From limitedLinear
   }
   ```

3. **Relax solver tolerances**
   ```cpp
   // system/fvSolution
   solvers
   {
       p
       {
           relTol          0.2;  // From 0.1, more relaxed
       }
   }
   ```

**การแก้:**

1. **ลด timestep**
2. **ใช้ scheme ที่เสถียรกว่า**
3. **ผ่อนคลาย solver tolerances**

---

### Issue 3: Excessive Disk Usage

**ปัญหา 3: การใช้ดิสก์มากเกินไป**

**Symptoms:**
- Disk quota exceeded
- Slow I/O performance
- Out of storage space

**อาการ:**
- เกินโควตาดิสก์
- ประสิทธิภาพ I/O ช้า
- พื้นที่เก็บข้อมูลหมด

**Solutions:**

1. **Enable compression**
   ```cpp
   writeCompression compressed;
   ```

2. **Reduce write frequency**
   ```cpp
   writeInterval   1.0;  // From 0.1
   ```

3. **Clean old time directories**
   ```bash
   # Keep only last 5 time directories
   foamListTimes -rm
   ```

4. **Write only essential fields**
   ```cpp
   fields          (p U);  // Not all fields
   ```

**การแก้:**

1. **เปิดการบีบอัด**
2. **ลดความถี่ในการเขียน**
3. **ลบไดเรกทอรีเวลาเก่า**
4. **เขียนเฉพาะ field ที่จำเป็น**

---

## 🎓 Key Takeaways

**สรุปสำคัญ**

### ✅ DO's

1. **Optimize I/O first** - Often the biggest bottleneck
2. **Use appropriate preconditioners** - GAMG for large cases, DIC for small
3. **Set realistic tolerances** - Not too tight, not too loose
4. **Enable compression** - Saves storage and I/O time
5. **Benchmark changes** - Measure improvements, don't guess
6. **Start with stable schemes** - upwind/Euler, then increase accuracy

### ❌ DON'Ts

1. **Don't change everything at once** - Isolate each optimization
2. **Don't use tight tolerances unnecessarily** - Wastes computational resources
3. **Don't ignore memory limits** - OOM errors waste time
4. **Don't use high-order schemes for production** - Unless verified stable
5. **Don't forget decomposition** - Affects both memory and load balance

**สิ่งที่ควรทำ:**

1. **ปรับแต่ง I/O ก่อน** - มักเป็นคอขวดใหญ่ที่สุด
2. **ใช้ preconditioner ที่เหมาะสม** - GAMG สำหรับกรณีใหญ่, DIC สำหรับเล็ก
3. **ตั้งค่า tolerance ที่เป็นจริง** - ไม่แน่นเกินไป, ไม่หลวมเกินไป
4. **เปิดการบีบอัด** - ประหยัดพื้นที่และเวลา I/O
5. **วัดการเปลี่ยนแปลง** - วัดการปรับปรุง, อย่าเดา
6. **เริ่มต้นด้วย scheme ที่เสถียร** - upwind/Euler, จากนั้นเพิ่มความแม่นยำ

**สิ่งที่ไม่ควรทำ:**

1. **อย่าเปลี่ยนทุกอย่างพร้อมกัน** - แยกการปรับแต่งแต่ละรายการ
2. **อย่าใช้ tolerance แน่นโดยไม่จำเป็น** - ทิ้งทรัพยากรการคำนวณ
3. **อย่าละเลยขีดจำกัดหน่วยความจำ** - OOM errors ทิ้งเวลา
4. **อย่าใช้ scheme ลำดับสูงสำหรับการผลิต** - เว้นแต่ยืนยันว่าเสถียร
5. **อย่าลืมการแยก** - ส่งผลต่อทั้งหน่วยความจำและความสมดุลโหลด

---

## 📖 Related Reading

**เอกสารที่เกี่ยวข้อง**

### Prerequisites

- **[00_Overview.md](00_Overview.md)** - High-performance computing concepts
- **[01_Domain_Decomposition.md](01_Domain_Decomposition.md)** - Decomposition methods (MOVED HERE)
- **[02_Performance_Monitoring.md](02_Performance_Monitoring.md)** - Load balancing (MOVED HERE)

### Further Reading

- **OpenFOAM User Guide:** Chapter 5 - Numerical Schemes
- **OpenFOAM Programmer's Guide:** Linear Solvers and Preconditioners
- **CFD Online:** [OpenFOAM Performance Tuning Forum](https://cfd-online.com/Forums/openfoam/)
- **HPC Best Practices:** Memory optimization and I/O optimization

---

## 📝 Self-Assessment

**การประเมินตนเอง**

<details>
<summary><b>1. เหตุใดการลดความถี่ในการเขียน (writeInterval) จึงช่วยเพิ่มประสิทธิภาพ?</b></summary>

**คำตอบ:**
- **WHAT:** การเขียนข้อมูลถี่เกินไปทำให้เกิด I/O operations มากเกินไป
- **WHY:** I/O เป็นคอขวดที่สำคัญ (30-50% ของเวลาทั้งหมด)
- **HOW:** เพิ่ม writeInterval ลดจำนวนครั้งการเขียน → ลดค่าใช้จ่าย I/O → การจำลองเร็วขึ้น
- **Trade-off:** ข้อมูล time history น้อยลง แต่สามารถบันทึกเฉพาะเวลาที่สนใจได้

</details>

<details>
<summary><b>2. แบบไหนของ preconditioner ควรใช้สำหรับเมชขนาดใหญ่ (> 5M cells)?</b></summary>

**คำตอบ:**
- **GAMG (Geometric-Algebraic Multi-Grid)**
- **Why:** ลด iterations อย่างมากสำหรับกรณีขนาดใหญ่ (50-80% ลดลง)
- **Trade-off:** ต้นทุนต่อ iteration สูงขึ้นและใช้หน่วยความจำมากขึ้น
- **เหมาะสมสำหรับ:** เมชขนาดใหญ่, สมการความดัน, ปัญหาที่มีคำตอบเรียบ
- **ไม่เหมาะสำหรับ:** เมชขนาดเล็ก (< 1M cells), เวลาเริ่มต้นสำคัญมาก

</details>

<details>
<summary><b>3. เมื่อไรควรใช้ 'upwind' scheme เทียบกับ 'limitedLinear'?</b></summary>

**คำตอบ:**
- **ใช้ upwind เมื่อ:**
  - การดีบักและต้องการเสถียรภาพ
  - การไหลที่มี shock หรือ discontinuities รุนแรง
  - timestep ขนาดใหญ่ (maxCo → 1.0)
  
- **ใช้ limitedLinear เมื่อ:**
  - การรันการผลิต (production runs)
  - ต้องการความแม่นยำลำดับสอง
  - เสถียรภาพเพียงพอ (ตรวจสอบ residuals)
  - ต้องการสมดุลระหว่างความแม่นยำและเสถียรภาพ

</details>

---

**End of Section: Optimization Techniques**

**จบส่วน: เทคนิคการปรับแต่งประสิทธิภาพ**