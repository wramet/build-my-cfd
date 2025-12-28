# Simulation Control

การควบคุมการจำลองใน OpenFOAM

---

## Overview

| File | Purpose |
|------|---------|
| `system/controlDict` | Time control, output, functions |
| `system/fvSolution` | Solvers, algorithms, relaxation |
| `system/fvSchemes` | Discretization schemes |

---

## 1. controlDict

### Basic Settings

```cpp
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1000;
deltaT          1;

writeControl    timeStep;
writeInterval   100;
purgeWrite      3;              // Keep only 3 latest results
runTimeModifiable true;         // Allow runtime modification
```

### Transient Settings

```cpp
application     pimpleFoam;
deltaT          0.001;
adjustTimeStep  yes;
maxCo           0.8;            // CFL < 1 for stability
maxDeltaT       0.01;
```

### CFL Condition

$$Co = \frac{|u| \Delta t}{\Delta x} < 1$$

---

## 2. fvSolution

### Linear Solvers

```cpp
solvers
{
    p
    {
        solver      GAMG;
        tolerance   1e-7;
        relTol      0.01;
        smoother    GaussSeidel;
    }
    
    U
    {
        solver      smoothSolver;
        smoother    GaussSeidel;
        tolerance   1e-8;
        relTol      0;
    }
    
    "(k|epsilon|omega)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-6;
        relTol          0;
    }
}
```

### Solver Selection

| Variable | Recommended | Why |
|----------|-------------|-----|
| p | `GAMG` | Fast for elliptic |
| U | `smoothSolver` | Non-symmetric |
| Turbulence | `PBiCGStab` | Robust |

### Under-Relaxation (SIMPLE)

```cpp
relaxationFactors
{
    fields    { p 0.3; }
    equations { U 0.7; "(k|epsilon)" 0.7; }
}
```

| Variable | Range | Effect |
|----------|-------|--------|
| p | 0.2-0.5 | Lower = more stable |
| U | 0.5-0.8 | Balance speed/stability |

### Algorithm Settings

```cpp
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    pRefCell    0;
    pRefValue   0;
    residualControl { p 1e-5; U 1e-5; }
}

PIMPLE
{
    nOuterCorrectors 2;
    nCorrectors      2;
    nNonOrthogonalCorrectors 1;
}
```

---

## 3. Convergence Monitoring

### Residual Targets

| Variable | Target |
|----------|--------|
| p | $10^{-6}$ |
| U | $10^{-7}$ |
| Turbulence | $10^{-5}$ |

### Function Objects

```cpp
functions
{
    residuals
    {
        type    residuals;
        fields  (p U k epsilon);
    }
    
    forces
    {
        type    forces;
        patches (airfoil);
        rhoInf  1.225;
    }
}
```

---

## 4. Troubleshooting

| Problem | Solution |
|---------|----------|
| Divergence | Lower relaxation factors |
| Slow convergence | Increase relaxation (carefully) |
| Oscillating residuals | Use 1st-order schemes first |
| High continuity error | Check mesh quality |

### Mesh Quality Check

```bash
checkMesh -allGeometry -allTopology
```

| Metric | Target |
|--------|--------|
| Non-orthogonality | < 70° |
| Skewness | < 0.5 |
| Aspect ratio | < 1000 |

---

## 5. Best Practices

1. **Start conservative**: Low relaxation, 1st-order schemes
2. **Monitor multiple quantities**: Residuals + physical values
3. **Check mesh before running**: `checkMesh`
4. **Use `purgeWrite`**: Save disk space
5. **Enable `runTimeModifiable`**: Adjust on-the-fly

---

## Concept Check

<details>
<summary><b>1. ทำไม SIMPLE ต้องใช้ under-relaxation?</b></summary>

เพราะ SIMPLE ไม่มี time derivative → ไม่มี natural damping → ค่าเปลี่ยนแปลงเร็วเกินไปอาจ diverge จึงต้องใช้ relaxation เพื่อลด update ในแต่ละ iteration
</details>

<details>
<summary><b>2. `relTol` vs `tolerance` ต่างกันอย่างไร?</b></summary>

- **tolerance**: Absolute residual target
- **relTol**: Relative reduction from initial residual

Solver หยุดเมื่อ **อย่างใดอย่างหนึ่ง** บรรลุ
</details>

<details>
<summary><b>3. ทำไม GAMG เร็วกว่า PCG สำหรับ pressure?</b></summary>

GAMG ใช้ **multigrid** — แก้ low-frequency errors บน coarse grids ได้เร็วกว่า ในขณะที่ PCG ต้องใช้ iterations มากกว่าสำหรับ global modes
</details>

---

## Related Documents

- **บทก่อนหน้า:** [02_Standard_Solvers.md](02_Standard_Solvers.md)
- **บทถัดไป:** [../02_PRESSURE_VELOCITY_COUPLING/00_Overview.md](../02_PRESSURE_VELOCITY_COUPLING/00_Overview.md)