# Best Practices

แนวปฏิบัติสำหรับ CFD Simulation ที่เสถียร แม่นยำ และมีประสิทธิภาพ

---

## Mesh Quality

### คุณภาพที่ต้องตรวจสอบ

| Parameter | Target | Critical | ผลกระทบ |
|-----------|--------|----------|---------|
| Non-orthogonality | < 50° | > 70° | Gradient accuracy |
| Skewness | < 0.5 | > 0.6 | Interpolation error |
| Aspect Ratio | < 10 | > 100 | จตุรัสเสถียรกว่า |
| Expansion Ratio | < 1.3 | > 1.5 | Numerical diffusion |

**ตรวจสอบ:**
```bash
checkMesh
```

### การแก้ไข

```cpp
// system/fvSolution — เพิ่ม non-orthogonal corrections
SIMPLE
{
    nNonOrthogonalCorrectors 2;  // 0 สำหรับ ortho, 2-3 สำหรับ non-ortho
}
```

---

## Scheme Selection

### Temporal (ddtSchemes)

| Scheme | Order | Stability | ใช้เมื่อ |
|--------|-------|-----------|---------|
| `Euler` | 1 | ดีมาก | เริ่มต้น, general |
| `backward` | 2 | ดี | ต้องการ accuracy |
| `CrankNicolson 0.5` | 2 | ปานกลาง | Waves |

### Convection (divSchemes)

| Pe (Peclet) | Scheme | เหตุผล |
|-------------|--------|--------|
| < 2 | `Gauss linear` | Accuracy สูง |
| 2-10 | `Gauss linearUpwind` | Balance |
| > 10 | `Gauss upwind` | Stability |

**Turbulence (k, ε, ω):** ใช้ `Gauss upwind` เสมอ

### Diffusion (laplacianSchemes)

```cpp
laplacianSchemes
{
    default         Gauss linear corrected;   // Ortho mesh
    // หรือ
    default         Gauss linear limited 0.5; // High non-ortho
}
```

### Gradient (gradSchemes)

```cpp
gradSchemes
{
    default         Gauss linear;             // Standard
    grad(U)         cellLimited Gauss linear 1;  // Limited
}
```

---

## Solver Settings

### Solver Selection

| Field | Solver | Preconditioner |
|-------|--------|----------------|
| p | `GAMG` | GaussSeidel |
| U | `PBiCGStab` | DILU |
| k, ε | `PBiCGStab` | DILU |
| T | `PBiCGStab` | DILU |

### Tolerance Guide

| Field | tolerance | relTol | หมายเหตุ |
|-------|-----------|--------|---------|
| p | 1e-6 | 0.01 | Tight |
| pFinal | 1e-6 | 0 | Very tight |
| U | 1e-5 | 0.1 | Moderate |
| k, ε | 1e-6 | 0.1 | Moderate |

### Relaxation Factors

| Field | Steady (SIMPLE) | Transient (PIMPLE) |
|-------|-----------------|-------------------|
| p | 0.3 | 0.7-1.0 |
| U | 0.7 | 0.9-1.0 |
| k, ε | 0.7 | 0.9-1.0 |

---

## Boundary Conditions

### Velocity

| Location | Type | ตัวอย่าง |
|----------|------|---------|
| Inlet | `fixedValue` | `uniform (10 0 0)` |
| Outlet | `zeroGradient` หรือ `pressureInletOutletVelocity` | — |
| Wall | `noSlip` | — |

### Pressure

| Location | Type | ตัวอย่าง |
|----------|------|---------|
| Inlet | `zeroGradient` | — |
| Outlet | `fixedValue` | `uniform 0` |
| Wall | `zeroGradient` | — |

### Turbulence Wall Functions

| y+ Range | Wall Function |
|----------|---------------|
| < 5 | Low-Re model (mesh ละเอียด) |
| 30-300 | `kqRWallFunction`, `epsilonWallFunction` |
| > 300 | Mesh หยาบเกินไป |

---

## Convergence Monitoring

### Residual Targets

| Field | Initial | Final | หมายเหตุ |
|-------|---------|-------|---------|
| p | 1e-2 | 1e-5 | ลด 3+ orders |
| U | 1e-2 | 1e-5 | ลด 3+ orders |
| k, ε | 1e-2 | 1e-5 | ต้องลดลง |

### ตรวจสอบ

```cpp
// system/controlDict
functions
{
    residuals
    {
        type            residuals;
        libs            (utilityFunctionObjects);
        writeControl    timeStep;
        fields          (p U k epsilon);
    }
}
```

```bash
# Plot residuals
foamLog log.simpleFoam
gnuplot residuals.gp
```

---

## Troubleshooting

### Divergence

| สาเหตุ | การแก้ไข |
|--------|---------|
| Δt ใหญ่เกินไป | ลด `deltaT`, ตั้ง `maxCo 0.5` |
| Relaxation สูงเกินไป | ลด p=0.2, U=0.5 |
| Mesh ไม่ดี | `checkMesh`, fix non-ortho |
| BC ไม่ถูกต้อง | ตรวจสอบ inlet/outlet pairing |
| Scheme ไม่เสถียร | เปลี่ยนเป็น upwind |

### Converge ช้า

| สาเหตุ | การแก้ไข |
|--------|---------|
| Relaxation ต่ำเกินไป | เพิ่ม p=0.4, U=0.8 |
| Solver tolerance | เพิ่ม relTol (0.01 → 0.1) |
| Initial conditions | เดิม fields จาก similar case |

### Accuracy ต่ำ

| สาเหตุ | การแก้ไข |
|--------|---------|
| Numerical diffusion | เปลี่ยน upwind → linearUpwind |
| Mesh หยาบ | Refine mesh |
| BCs ผิด | ตรวจสอบ physics |

---

## Parallel Computing

### Setup

```cpp
// system/decomposeParDict
numberOfSubdomains  8;
method              scotch;  // หรือ hierarchical
```

### Run

```bash
decomposePar
mpirun -np 8 simpleFoam -parallel
reconstructPar
```

### Guidelines

- 10,000-50,000 cells ต่อ processor
- ใช้ `scotch` สำหรับ complex geometry
- ใช้ `hierarchical` สำหรับ structured mesh

---

## Pre-Run Checklist

✅ `checkMesh` passes with no errors
✅ BCs consistent (p zeroGradient where U fixed, etc.)
✅ Initial fields reasonable
✅ Time step gives Co < 1 (transient) หรือ stable residuals (steady)
✅ Schemes appropriate for flow regime
✅ Solver tolerances set correctly

---

## Concept Check

<details>
<summary><b>1. Mesh non-orthogonality สูง ต้องทำอย่างไร?</b></summary>

1. เพิ่ม `nNonOrthogonalCorrectors` ใน fvSolution
2. ใช้ `limited` correction ใน laplacianSchemes
3. ลอง `leastSquares` ใน gradSchemes
</details>

<details>
<summary><b>2. Simulation diverge ทันทีที่เริ่ม ควรตรวจอะไร?</b></summary>

1. Initial conditions (ค่า 0 ที่ไม่ควรเป็น 0?)
2. Boundary conditions (consistent pairing?)
3. Time step (ใหญ่เกินไป?)
4. Mesh quality (`checkMesh`)
</details>

<details>
<summary><b>3. Residual ลดลงแล้วหยุด ไม่ลดต่อ ทำอย่างไร?</b></summary>

1. ตรวจ mass balance
2. ดู field monitoring — อาจ converged แล้ว
3. ลอง tighten tolerances
4. ตรวจ BCs — อาจมี conflict
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [06_OpenFOAM_Implementation.md](06_OpenFOAM_Implementation.md) — OpenFOAM Implementation
- **บทถัดไป:** [08_Exercises.md](08_Exercises.md) — แบบฝึกหัด