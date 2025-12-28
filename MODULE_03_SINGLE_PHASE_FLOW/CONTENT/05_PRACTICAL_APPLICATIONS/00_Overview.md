# Practical Applications Overview

การประยุกต์ใช้ OpenFOAM ในงานวิศวกรรมจริง

> **ทำไมต้องเรียนบทนี้?**
> - **เชื่อมโยง theory กับงานจริง** — aerodynamics, piping, heat exchangers
> - รู้ **engineering metrics** ที่สำคัญ — $C_D$, $\Delta p$, $Nu$
> - ใช้ **function objects** คำนวณค่าระหว่าง simulation

---

## Workflow

> **💡 CFD Workflow ทั่วไป:**
>
> Physics → Solver → Mesh → BCs → Run → Post-process → Validate

```mermaid
flowchart LR
    A[Physics] --> B[Solver Selection]
    B --> C[Mesh]
    C --> D[Boundary Conditions]
    D --> E[Run]
    E --> F[Post-Process]
    F --> G[Validate]
```

---

## 1. Application Categories

| Category | Solver | Key Metrics |
|----------|--------|-------------|
| **External Aerodynamics** | `simpleFoam`, `pimpleFoam` | $C_D$, $C_L$, $C_p$ |
| **Internal Flow** | `simpleFoam`, `pimpleFoam` | $\Delta p$, $f$, $Re$ |
| **Heat Exchangers** | `chtMultiRegionFoam` | $U$, $\varepsilon$, $Nu$ |
| **Mixing** | `scalarTransportFoam` | CoV, RTD |

---

## 2. Solver Selection Guide

### By Flow Type

| Flow | Condition | Solver |
|------|-----------|--------|
| Incompressible | Steady | `simpleFoam` |
| Incompressible | Transient | `pimpleFoam` |
| Heat transfer | Buoyancy | `buoyantSimpleFoam` |
| Heat transfer | CHT | `chtMultiRegionFoam` |
| Mixing | Passive scalar | `scalarTransportFoam` |

### By Application

| Application | Recommended Solver |
|-------------|-------------------|
| Vehicle aerodynamics | `simpleFoam` + k-ω SST |
| Pipe flow | `simpleFoam` + k-ε |
| Heat exchanger | `chtMultiRegionFoam` |
| Stirred tank | `SRFSimpleFoam` หรือ `pimpleDyMFoam` |

---

## 3. Key Engineering Metrics

### Pressure Drop

$$\Delta p = p_{inlet} - p_{outlet}$$
$$K = \frac{\Delta p}{0.5 \rho U^2}$$

### Force Coefficients

$$C_D = \frac{F_D}{0.5 \rho U_\infty^2 A}$$
$$C_L = \frac{F_L}{0.5 \rho U_\infty^2 A}$$

### Heat Transfer

$$Nu = \frac{hL}{k}$$
$$h = \frac{q''}{T_s - T_\infty}$$

### Mixing

$$CoV = \frac{\sigma_c}{\bar{c}}$$
$$MI = 1 - \frac{\sigma}{\sigma_0}$$

---

## 4. Common Function Objects

```cpp
// system/controlDict
functions
{
    forces
    {
        type    forces;
        patches (body);
        rhoInf  1.225;
        CofR    (0 0 0);
    }
    
    forceCoeffs
    {
        type    forceCoeffs;
        patches (body);
        rhoInf  1.225;
        lRef    1.0;
        Aref    1.0;
        liftDir (0 1 0);
        dragDir (1 0 0);
    }
    
    pressureDrop
    {
        type    surfaceFieldValue;
        operation areaAverage;
        patches (inlet);
        fields  (p);
    }
}
```

---

## 5. Mesh Requirements

| Application | $y^+$ Target | Mesh Type |
|-------------|--------------|-----------|
| Aerodynamics | 1 or 30-100 | snappyHexMesh |
| Pipe flow | 30-300 | blockMesh |
| Heat transfer | 1-5 | Boundary layers |
| Mixing | 30-100 | Structured |

---

## 6. Typical Workflow

1. **Geometry**: CAD → STL export
2. **Background mesh**: `blockMesh`
3. **Snapping**: `snappyHexMesh`
4. **Check quality**: `checkMesh`
5. **Set BCs**: `0/` directory
6. **Run solver**: `simpleFoam` / `pimpleFoam`
7. **Post-process**: `paraFoam`, function objects
8. **Validate**: Compare with experiment/correlations

---

## Concept Check

<details>
<summary><b>1. ทำไมต้องเลือก Solver ให้ตรงกับ physics?</b></summary>

เพราะแต่ละ solver ถูกออกแบบมาสำหรับสมการที่ต่างกัน — เช่น `simpleFoam` ไม่มี energy equation ถ้าต้องการ heat transfer ต้องใช้ `buoyantSimpleFoam`
</details>

<details>
<summary><b>2. Force coefficients ($C_D$, $C_L$) ใช้ทำอะไร?</b></summary>

เป็นค่าไร้มิติที่ใช้เปรียบเทียบ performance ระหว่างการออกแบบต่างๆ หรือเทียบกับ experiment/literature ได้ง่ายกว่าแรงสัมบูรณ์
</details>

<details>
<summary><b>3. Function objects ช่วยอะไร?</b></summary>

คำนวณค่าสำคัญ **ระหว่างการจำลอง** โดยอัตโนมัติ ไม่ต้อง post-process ทีหลัง — เช่น $C_D$, $\Delta p$, heat flux
</details>

---

## Related Documents

- **บทถัดไป:** [01_External_Aerodynamics.md](01_External_Aerodynamics.md)
- **Internal Flow:** [02_Internal_Flow_and_Piping.md](02_Internal_Flow_and_Piping.md)
- **Heat Exchangers:** [03_Heat_Exchangers.md](03_Heat_Exchangers.md)