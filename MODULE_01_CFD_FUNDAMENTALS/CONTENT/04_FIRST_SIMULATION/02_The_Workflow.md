# CFD Simulation Workflow

รายละเอียดของ 3 ขั้นตอนหลัก: Pre-processing, Solving, Post-processing

> **ทำไมต้องรู้ workflow ละเอียด?**
> - แต่ละขั้นตอนใช้ **ไฟล์และ tools ต่างกัน**
> - ถ้า simulation ไม่ work → รู้ว่าต้อง debug ขั้นตอนไหน
> - เข้าใจ workflow = ทำงานได้เร็วขึ้น

---

## 1. Pre-Processing

### 1.1 Geometry & Mesh

**blockMesh** สร้าง structured mesh:

```cpp
// constant/polyMesh/blockMeshDict
vertices
(
    (0 0 0)
    (1 0 0)
    (1 1 0)
    (0 1 0)
    (0 0 0.1)
    (1 0 0.1)
    (1 1 0.1)
    (0 1 0.1)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 1) simpleGrading (1 1 1)
);

boundary
(
    movingWall  { type wall; faces ((3 7 6 2)); }
    fixedWalls  { type wall; faces ((0 4 7 3) (2 6 5 1) (1 5 4 0)); }
    frontAndBack { type empty; faces ((0 3 2 1) (4 5 6 7)); }
);
```

**ตรวจสอบ Mesh:**

```bash
checkMesh
```

| Metric | Good | Acceptable | Bad |
|--------|------|------------|-----|
| Non-orthogonality | < 50° | 50-70° | > 70° |
| Skewness | < 2 | 2-4 | > 4 |
| Aspect ratio | < 10 | 10-100 | > 100 |

### 1.2 Boundary Conditions

**Velocity (0/U):**

```cpp
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);

boundaryField
{
    movingWall
    {
        type    fixedValue;
        value   uniform (1 0 0);
    }
    fixedWalls
    {
        type    noSlip;
    }
    frontAndBack
    {
        type    empty;
    }
}
```

**Pressure (0/p):**

```cpp
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    movingWall   { type zeroGradient; }
    fixedWalls   { type zeroGradient; }
    frontAndBack { type empty; }
}
```

### 1.3 Properties

```cpp
// constant/transportProperties
transportModel  Newtonian;
nu              [0 2 -1 0 0 0 0] 0.01;  // Re = UL/ν = 100
```

---

## 2. Solving

### 2.1 Solver Configuration

**system/controlDict:**

```cpp
application     icoFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         0.5;
deltaT          0.005;
writeControl    timeStep;
writeInterval   20;
```

**system/fvSchemes:**

```cpp
ddtSchemes      { default Euler; }
gradSchemes     { default Gauss linear; }
divSchemes      { div(phi,U) Gauss upwind; }
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
```

**system/fvSolution:**

```cpp
solvers
{
    p
    {
        solver      GAMG;
        tolerance   1e-06;
        relTol      0.01;
        smoother    GaussSeidel;
    }
    U
    {
        solver      smoothSolver;
        smoother    GaussSeidel;
        tolerance   1e-05;
        relTol      0;
    }
}

PISO
{
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}
```

### 2.2 Running

```bash
# Serial
icoFoam > log.icoFoam 2>&1 &

# Monitor
tail -f log.icoFoam

# Check convergence
grep "Initial residual" log.icoFoam
```

### 2.3 Convergence

**เกณฑ์:**
- Residuals ลด 3-4 orders of magnitude
- Solution ไม่เปลี่ยนแปลงมาก (steady state)

**ปัญหาที่พบบ่อย:**

| ปัญหา | สาเหตุ | แก้ไข |
|-------|--------|-------|
| Diverge | Time step ใหญ่เกินไป | ลด deltaT |
| ไม่ converge | BC ไม่ consistent | ตรวจ U-p pairing |
| Oscillate | Scheme ไม่เสถียร | เปลี่ยนเป็น upwind |

---

## 3. Post-Processing

### 3.1 Visualization (ParaView)

```bash
paraFoam
```

**สิ่งที่ควรดู:**
1. **Velocity magnitude** — ตรวจ max/min
2. **Streamlines** — ดู flow pattern
3. **Pressure contours** — ตรวจ distribution
4. **Animation** — ดู time evolution

### 3.2 Quantitative Analysis

**Probes:**

```cpp
// system/controlDict
functions
{
    probes
    {
        type            probes;
        libs            (sampling);
        writeControl    timeStep;
        writeInterval   1;
        fields          (U p);
        probeLocations  ((0.5 0.5 0.05));
    }
}
```

**Sample lines:**

> **⚠️ หมายเหตุ:** ใน OpenFOAM รุ่นใหม่ ใช้ `functions` ใน `controlDict` แทน `sampleDict`

**วิธีที่ 1: ใช้ controlDict functions (แนะนำสำหรับ OpenFOAM v4+)**

```cpp
// system/controlDict
functions
{
    centerlineY
    {
        type            sets;
        setFormat       raw;
        fields          (U p);
        interpolationScheme cellPoint;

        sets
        (
            centerlineY
            {
                type    uniform;
                axis    y;
                start   (0.5 0 0.05);
                end     (0.5 1 0.05);
                nPoints 100;
            }
        );
    }
}
```

**วิธีที่ 2: ใช้ postProcess กับ function name**

```bash
# Run หลัง simulation จบ
postProcess -func centerlineY
```

ผลลัพธ์จะอยู่ที่ `postProcessing/centerlineY/`

---

## Workflow Summary

```bash
#!/bin/bash
# Allrun script

# 1. Clean
foamCleanTutorials  # ใช้ได้เฉพาะกับ tutorials จาก $FOAM_TUTORIALS
# หรือสำหรับ custom case:
# rm -rf 0/*/processor* */postProcessing/ [0-9]*/

# 2. Mesh
blockMesh
checkMesh

# 3. Solve
icoFoam > log.icoFoam 2>&1

# 4. Post-process
paraFoam
```

---

## Concept Check

<details>
<summary><b>1. ทำไม empty BC ใช้กับ frontAndBack?</b></summary>

เพราะเป็น 2D simulation — ไม่มี variation ในทิศทาง z ดังนั้น solver ไม่ต้องแก้สมการในทิศทางนั้น
</details>

<details>
<summary><b>2. PISO nCorrectors คืออะไร?</b></summary>

จำนวนรอบการแก้ไข pressure-velocity coupling ต่อ time step — ค่า 2-3 เพียงพอสำหรับกรณีส่วนใหญ่
</details>

<details>
<summary><b>3. pRefCell และ pRefValue ทำไมต้องกำหนด?</b></summary>

ใน incompressible flow ค่า absolute pressure ไม่สำคัญ (สมการมีเฉพาะ ∇p) → ต้อง fix ค่าที่ 1 cell เพื่อให้ solution unique
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_Introduction.md](01_Introduction.md) — บทนำ
- **บทถัดไป:** [03_The_Lid-Driven_Cavity_Problem.md](03_The_Lid-Driven_Cavity_Problem.md) — Cavity Problem