# LES Fundamentals

Large Eddy Simulation สำหรับการจำลองความปั่นป่วน

---

## Overview

**LES** แก้สมการสำหรับ large eddies โดยตรง และใช้ SGS model สำหรับ small eddies:

| Approach | Resolved | Modeled | Cost |
|----------|----------|---------|------|
| DNS | All scales | None | Highest |
| **LES** | Large eddies | Small eddies (SGS) | High |
| RANS | None | All scales | Lowest |

---

## 1. Spatial Filtering

### Filter Width

$$\Delta = \sqrt[3]{V_{cell}}$$

```cpp
// constant/turbulenceProperties
LES
{
    delta   cubeRootVol;  // หรือ maxDeltaxyz
}
```

### Filtered Equations

$$\frac{\partial \bar{u}_i}{\partial t} + \frac{\partial}{\partial x_j}(\bar{u}_i \bar{u}_j) = -\frac{1}{\rho}\frac{\partial \bar{p}}{\partial x_i} + \nu \frac{\partial^2 \bar{u}_i}{\partial x_j^2} - \frac{\partial \tau_{ij}^{SGS}}{\partial x_j}$$

**SGS Stress Tensor:**
$$\tau_{ij}^{SGS} = \overline{u_i u_j} - \bar{u}_i \bar{u}_j$$

---

## 2. SGS Models

### Model Comparison

| Model | Formula | Use Case |
|-------|---------|----------|
| **Smagorinsky** | $\nu_{SGS} = (C_s \Delta)^2 |\bar{S}|$ | Simple, stable |
| **WALE** | Auto wall behavior | Wall-bounded |
| **Dynamic** | Computes $C_s$ automatically | Complex flows |
| **oneEqEddy** | Solves k equation | General purpose |

### Smagorinsky

```cpp
// constant/turbulenceProperties
simulationType  LES;

LES
{
    LESModel        Smagorinsky;
    turbulence      on;
    delta           cubeRootVol;
    
    SmagorinskyCoeffs
    {
        Cs      0.1;    // 0.1-0.2
    }
}
```

### WALE (Wall-Adaptive)

```cpp
LES
{
    LESModel        WALE;
    delta           cubeRootVol;
    
    WALECoeffs
    {
        Cw      0.325;
    }
}
```

### Dynamic Smagorinsky

```cpp
LES
{
    LESModel        dynamicSmagorinsky;
    delta           cubeRootVol;
    // Cs computed automatically
}
```

---

## 3. Boundary Conditions

### Inlet

```cpp
// 0/U - Turbulent inlet
inlet
{
    type            turbulentInlet;
    mean            (10 0 0);
    fluctuation     (0.5 0.5 0.5);
}

// Alternative: Synthetic Eddy Method
inlet
{
    type            turbulentDFSEMInlet;
    delta           0.01;
    nEddy           100;
}
```

### Outlet

```cpp
outlet
{
    type            zeroGradient;
}
```

### Wall

```cpp
// Wall-resolved (y+ ≈ 1)
walls
{
    type            noSlip;
}

// 0/nut
walls
{
    type            nutLowReWallFunction;
    value           uniform 0;
}
```

---

## 4. Mesh Requirements

### Resolution Guidelines

| Region | Requirement |
|--------|-------------|
| $\Delta x^+$ | 40-60 (streamwise) |
| $\Delta z^+$ | 15-20 (spanwise) |
| $\Delta y^+$ | ≈ 1 (wall-normal) |

### $y^+$ Target

| LES Type | $y^+$ | Cells in BL |
|----------|-------|-------------|
| Wall-resolved | ≈ 1 | 10-15 |
| Wall-modeled | 50-200 | 5-8 |

### CFL Requirement

$$CFL = \frac{|u| \Delta t}{\Delta x} < 0.5$$

```cpp
// system/controlDict
adjustTimeStep  yes;
maxCo           0.5;
```

---

## 5. Solver Settings

### fvSchemes

```cpp
ddtSchemes
{
    default     backward;   // Second-order time
}

divSchemes
{
    div(phi,U)  Gauss linear;  // Low-dissipation
}

laplacianSchemes
{
    default     Gauss linear corrected;
}
```

### fvSolution

```cpp
PIMPLE
{
    nOuterCorrectors    1;
    nCorrectors         2;
    nNonOrthogonalCorrectors 1;
}

solvers
{
    p
    {
        solver      GAMG;
        tolerance   1e-6;
        relTol      0.01;
    }
    U
    {
        solver      PBiCGStab;
        preconditioner DILU;
        tolerance   1e-5;
        relTol      0.1;
    }
}
```

---

## 6. Quality Metrics

### SGS Resolution Index

$$\eta = \frac{\nu_{SGS}}{\nu + \nu_{SGS}}$$

| $\eta$ | Quality |
|--------|---------|
| < 0.2 | Good |
| 0.2-0.5 | Acceptable |
| > 0.5 | Needs finer mesh |

### Energy Spectrum

- Should show $k^{-5/3}$ in inertial range
- Cutoff before dissipation range

---

## 7. Workflow

```bash
# 1. Generate fine mesh
blockMesh
checkMesh

# 2. Set turbulenceProperties to LES
# 3. Set appropriate schemes (low dissipation)

# 4. Run with pimpleFoam
pimpleFoam > log.pimpleFoam &

# 5. Monitor Courant number
tail -f log.pimpleFoam | grep "Courant"

# 6. Post-process statistics
postProcess -func fieldAverage
```

---

## Concept Check

<details>
<summary><b>1. LES ต่างจาก RANS อย่างไร?</b></summary>

- **LES:** แก้สมการสำหรับ large eddies โดยตรง ใช้ model เฉพาะ small eddies → จับ transient structures ได้ดี แต่ต้องการ mesh ละเอียดมาก
- **RANS:** เฉลี่ยทุก scales → เร็วกว่ามากแต่เห็นเฉพาะ mean flow
</details>

<details>
<summary><b>2. WALE ดีกว่า Smagorinsky ตรงไหน?</b></summary>

WALE ให้ $\nu_{SGS} \to 0$ ใกล้ผนังโดยอัตโนมัติ — ไม่ต้องใช้ damping functions เหมือน Smagorinsky ทำให้เหมาะกับ wall-bounded flows
</details>

<details>
<summary><b>3. ทำไม LES ต้องการ CFL < 1?</b></summary>

เพราะ LES ต้องการ temporal accuracy สูงเพื่อจับ transient structures ที่เคลื่อนที่ผ่าน mesh — CFL สูงเกินไปจะทำให้ eddies ถูก smeared หรือหายไป
</details>

---

## Related Documents

- **บทก่อนหน้า:** [03_Wall_Treatment.md](03_Wall_Treatment.md)
- **บทถัดไป:** [05_Validation_Best_Practices.md](05_Validation_Best_Practices.md)