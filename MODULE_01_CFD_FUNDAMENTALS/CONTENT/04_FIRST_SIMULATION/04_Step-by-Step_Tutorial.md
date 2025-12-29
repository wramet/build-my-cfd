# Step-by-Step Tutorial: Lid-Driven Cavity

Hands-on tutorial สำหรับ OpenFOAM

> **ทำไมต้องทำ Tutorial นี้?**
> - ฝึก **workflow จริง** ตั้งแต่ต้นจนจบ
> - เข้าใจ **case structure** ของ OpenFOAM
> - มีพื้นฐานสำหรับ modify และสร้าง case ใหม่

---

## Preparation

```bash
# Copy tutorial case
cp -r $FOAM_TUTORIALS/incompressible/icoFoam/cavity/cavity .
cd cavity
```

---

## Step 1: Review Case Structure

```bash
ls -la
# 0/
# constant/
# system/
```

---

## Step 2: Examine Mesh Definition

```bash
cat constant/polyMesh/blockMeshDict
```

```cpp
vertices
(
    (0 0 0)      // vertex 0
    (1 0 0)      // vertex 1
    (1 1 0)      // vertex 2
    (0 1 0)      // vertex 3
    (0 0 0.1)    // vertex 4
    (1 0 0.1)    // vertex 5
    (1 1 0.1)    // vertex 6
    (0 1 0.1)    // vertex 7
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 1) simpleGrading (1 1 1)
);

boundary
(
    movingWall
    {
        type wall;
        faces ((3 7 6 2));
    }
    fixedWalls
    {
        type wall;
        faces
        (
            (0 4 7 3)
            (2 6 5 1)
            (1 5 4 0)
        );
    }
    frontAndBack
    {
        type empty;
        faces
        (
            (0 3 2 1)
            (4 5 6 7)
        );
    }
);
```

---

## Step 3: Generate Mesh

```bash
blockMesh
```

**Output:**
```
Creating block mesh from "constant/polyMesh/blockMeshDict"
Creating topology blocks
Creating block mesh topology
...
Writing polyMesh
```

---

## Step 4: Check Mesh Quality

```bash
checkMesh
```

**Expected output:**
```
Mesh stats
    points:           882
    internal points:  0
    faces:            1640
    internal faces:   760
    cells:            400
    faces per cell:   6
    boundary patches: 3
    ...
Mesh OK.
```

---

## Step 5: Examine Boundary Conditions

**0/U:**
```cpp
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);

boundaryField
{
    movingWall
    {
        type            fixedValue;
        value           uniform (1 0 0);
    }
    fixedWalls
    {
        type            noSlip;
    }
    frontAndBack
    {
        type            empty;
    }
}
```

**0/p:**
```cpp
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    movingWall
    {
        type            zeroGradient;
    }
    fixedWalls
    {
        type            zeroGradient;
    }
    frontAndBack
    {
        type            empty;
    }
}
```

---

## Step 6: Set Fluid Properties

```bash
cat constant/transportProperties
```

```cpp
transportModel  Newtonian;
nu              [0 2 -1 0 0 0 0] 0.01;
```

**Reynolds Number:**
$$Re = \frac{UL}{\nu} = \frac{1 \times 1}{0.01} = 100$$

---

## Step 7: Configure Solver

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
ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss linear;      // 2nd order, accurate สำหรับ laminar flow
    // หากใช้ Re สูงๆ อาจต้องเปลี่ยนเป็น:
    // div(phi,U) Gauss linearUpwind grad(U);  // 2nd order + stable
    // หรือ:
    // div(phi,U) Gauss upwind;                 // 1st order + very stable
}

laplacianSchemes
{
    default         Gauss linear orthogonal;
}
```

**system/fvSolution:**
```cpp
solvers
{
    p
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-06;
        relTol          0.05;
    }

    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0;
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

---

## Step 8: Run Simulation

```bash
icoFoam > log.icoFoam 2>&1 &
```

**Monitor:**
```bash
tail -f log.icoFoam
```

**Check residuals:**
```bash
grep "Solving for p" log.icoFoam | tail -20
```

---

## Step 9: Visualize Results

```bash
paraFoam
```

**ใน ParaView:**
1. Click "Apply" (ปุ่มสีเขียวด้านบน) → แสดง mesh
2. เลือก "U" → Surface with Edges → แสดง velocity magnitude เป็นสี
3. เลือก "U" → Glyph → แสดง velocity vectors (ลูกศร)
4. Filter → Stream Tracer (หรือ Streamlines) → แสดง pathlines

**เคล็ดลับ:**
- ใช้ **Color by** → **U** → **Magnitude** เพื่อดู velocity distribution
- ใช้ **Rescale to Custom Range** ปรับ scale สีให้ชัดเจน
- บันทึกภาพ: **File** → **Export Screenshot...** หรือกด `Ctrl+E`

---

## Step 10: Extract Data for Validation

**เพิ่มใน system/controlDict:**
```cpp
functions
{
    fieldAverage1
    {
        type            fieldAverage;
        libs            (fieldFunctionObjects);
        writeControl    writeTime;
        fields
        (
            U { mean on; prime2Mean on; base time; }
            p { mean on; prime2Mean on; base time; }
        );
    }
    
    sample1
    {
        type            sets;
        libs            (sampling);
        writeControl    writeTime;
        
        interpolationScheme cellPoint;
        setFormat       raw;
        
        sets
        (
            centerlineX
            {
                type    uniform;
                axis    y;
                start   (0.5 0 0.05);
                end     (0.5 1 0.05);
                nPoints 100;
            }
            centerlineY
            {
                type    uniform;
                axis    x;
                start   (0 0.5 0.05);
                end     (1 0.5 0.05);
                nPoints 100;
            }
        );
        
        fields (U p);
    }
}
```

```bash
# Re-run or post-process
icoFoam
# or
postProcess -func sample1
```

---

## Quick Parameter Variations

### Change Reynolds Number

```bash
# Edit transportProperties
sed -i 's/nu.*/nu [0 2 -1 0 0 0 0] 0.001;/' constant/transportProperties
# Now Re = 1000
```

### Change Mesh Resolution

```bash
# Edit blockMeshDict
sed -i 's/(20 20 1)/(40 40 1)/' constant/polyMesh/blockMeshDict
blockMesh
```

### Longer Simulation

```bash
# Edit controlDict
sed -i 's/endTime.*/endTime 2.0;/' system/controlDict
```

---

## Troubleshooting

| ปัญหา | สาเหตุ | แก้ไข |
|-------|--------|-------|
| "FOAM FATAL ERROR" | Mesh ไม่ถูกสร้าง | `blockMesh` ก่อน |
| Divergence | Time step ใหญ่เกินไป | ลด deltaT |
| ผลลัพธ์ผิด | Re สูง + mesh หยาบ | เพิ่ม resolution |

---

## Concept Check

<details>
<summary><b>1. ทำไมใช้ empty BC สำหรับ frontAndBack?</b></summary>

เพราะเป็น 2D simulation — mesh มี 1 cell ในทิศ z และ empty บอก solver ว่าไม่ต้องแก้สมการในทิศทางนั้น
</details>

<details>
<summary><b>2. pRefCell 0 หมายความว่าอะไร?</b></summary>

Fix pressure ที่ cell index 0 ให้เท่ากับ pRefValue (0) — จำเป็นเพราะ incompressible flow กำหนด p ได้ถึง constant
</details>

<details>
<summary><b>3. ทำไมใช้ Gauss linear สำหรับ div(phi,U)?</b></summary>

Second-order accurate สำหรับ convection term — ถ้า unstable ให้ใช้ `Gauss upwind` แทน
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [03_The_Lid-Driven_Cavity_Problem.md](03_The_Lid-Driven_Cavity_Problem.md) — Problem
- **บทถัดไป:** [05_Expected_Results.md](05_Expected_Results.md) — Expected Results