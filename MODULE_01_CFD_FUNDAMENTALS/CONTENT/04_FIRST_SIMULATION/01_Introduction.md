# บทนำ: CFD Simulation Workflow

OpenFOAM CFD workflow และ components หลัก

> **ทำไมต้องเข้าใจ Workflow?**
> - CFD = **Pre-processing + Solving + Post-processing**
> - ถ้าไม่เข้าใจขั้นตอน → จะไม่รู้ว่าต้องแก้ไฟล์ไหนเมื่อมีปัญหา
> - เข้าใจ workflow = เข้าใจ **case structure** ของ OpenFOAM

---

## CFD คืออะไร?

**Computational Fluid Dynamics** — แก้สมการการไหลด้วยวิธีเชิงตัวเลข

$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu\nabla^2\mathbf{u}$$

แทนที่จะแก้แบบ analytical (ซึ่งเป็นไปไม่ได้สำหรับปัญหาจริง) → **discretize** สมการบน mesh แล้วแก้เชิงตัวเลข

---

## OpenFOAM Workflow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  PRE-PROCESSING │ → │     SOLVING     │ → │ POST-PROCESSING │
│  • Geometry     │    │  • icoFoam      │    │  • ParaView     │
│  • Mesh         │    │  • simpleFoam   │    │  • Probes       │
│  • BCs          │    │  • pimpleFoam   │    │  • Sampling     │
│  • Properties   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 1. Pre-Processing

### ไฟล์ที่ต้องเตรียม

| Directory | ไฟล์ | หน้าที่ |
|-----------|------|--------|
| `0/` | U, p, T, k, ε... | Initial & Boundary Conditions |
| `constant/` | polyMesh/, transportProperties | **Mesh** (points, faces, cells) & Physical properties |
| `system/` | controlDict, fvSchemes, fvSolution | Solver Settings |

> **💡 `constant/polyMesh/` คืออะไร?**
> - **`points`**: พิกัด (x,y,z) ของทุก vertices
> - **`faces`**: ผิว (2D) ที่เกิดจากการเชื่อม vertices
> - **`cells`**: volumes 3D ที่เกิดจาก faces
> - **`boundary`**: ชื่อ patches และ types (wall, patch, symmetry, ฯลฯ)

### สร้าง Mesh

```bash
# Simple geometries
blockMesh

# Complex geometries
snappyHexMesh -overwrite

# Check quality
checkMesh
```

### กำหนด Boundary Conditions

```cpp
// 0/U
inlet  { type fixedValue; value uniform (10 0 0); }
outlet { type zeroGradient; }
walls  { type noSlip; }
```

---

## 2. Solving

### เลือก Solver

| Solver | Use Case |
|--------|----------|
| `icoFoam` | Incompressible, laminar, transient |
| `simpleFoam` | Incompressible, turbulent, steady |
| `pimpleFoam` | Incompressible, turbulent, transient |
| `buoyantSimpleFoam` | Buoyancy, heat transfer, steady |

### รัน Simulation

```bash
# Serial
icoFoam > log.icoFoam &

# Monitor residuals
tail -f log.icoFoam

# Parallel (4 cores)
decomposePar
mpirun -np 4 icoFoam -parallel
reconstructPar
```

---

## 3. Post-Processing

### ParaView

```bash
paraFoam
```

**แสดงผล:**
- Velocity vectors
- Pressure contours
- Streamlines
- Iso-surfaces

### Quantitative Data

```cpp
// system/controlDict
functions
{
    probes
    {
        type        probes;
        fields      (U p);
        probeLocations ((0.5 0.5 0.05));
    }
}
```

---

## Case Directory Structure

```
myCase/
├── 0/
│   ├── U
│   └── p
├── constant/
│   ├── polyMesh/
│   │   ├── blockMeshDict
│   │   ├── boundary
│   │   ├── faces
│   │   ├── neighbour
│   │   ├── owner
│   │   └── points
│   └── transportProperties
├── system/
│   ├── controlDict
│   ├── fvSchemes
│   └── fvSolution
└── Allrun    # Run script (optional)
```

---

## Essential Files

### system/controlDict

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

### system/fvSchemes

```cpp
ddtSchemes      { default Euler; }
gradSchemes     { default Gauss linear; }
divSchemes      { div(phi,U) Gauss upwind; }
laplacianSchemes { default Gauss linear corrected; }
```

### system/fvSolution

```cpp
solvers
{
    p  { solver GAMG; tolerance 1e-6; relTol 0.01; }
    U  { solver smoothSolver; smoother GaussSeidel; tolerance 1e-5; relTol 0; }
}
PISO { nCorrectors 2; pRefCell 0; pRefValue 0; }
```

---

## Convergence Monitoring

### Residuals

```bash
# ดู residuals
grep "Solving for" log.icoFoam

# Plot ด้วย foamLog และ gnuplot
foamLog log.icoFoam
gnuplot
gnuplot> plot "logs/p_0" with lines
```

**เกณฑ์:**
- Initial residual ลดลง 3-4 orders of magnitude
- Final residual < tolerance ที่กำหนด

---

## Concept Check

<details>
<summary><b>1. ถ้า residuals ไม่ลดลง ควรตรวจอะไร?</b></summary>

1. Mesh quality (`checkMesh`)
2. Boundary conditions (U-p consistency)
3. Time step (CFL condition)
4. Discretization schemes
</details>

<details>
<summary><b>2. pRefCell และ pRefValue ใช้ทำไม?</b></summary>

ใน incompressible flow pressure ถูกกำหนดได้ถึง constant เท่านั้น → ต้อง fix ค่าที่ cell ใดเซลล์หนึ่ง
</details>

<details>
<summary><b>3. Gauss upwind กับ Gauss linear ต่างกันอย่างไร?</b></summary>

- `Gauss upwind`: 1st order, stable, diffusive
- `Gauss linear`: 2nd order, accurate, may oscillate at high Pe
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [00_Overview.md](00_Overview.md) — ภาพรวม
- **บทถัดไป:** [02_The_Workflow.md](02_The_Workflow.md) — Workflow Details