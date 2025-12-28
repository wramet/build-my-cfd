# External Aerodynamics

การจำลองพลศาสตร์อากาศภายนอกใน OpenFOAM

---

## Overview

**เป้าหมาย:** ทำนาย Drag ($C_D$) และ Lift ($C_L$) ด้วยความแม่นยำสูง

**ความท้าทาย:**
- Mesh resolution ใน boundary layer ($y^+$)
- Turbulence model สำหรับ flow separation
- Wake capturing

---

## 1. Key Parameters

### Force Coefficients

$$C_D = \frac{F_D}{0.5 \rho U_\infty^2 A}, \quad C_L = \frac{F_L}{0.5 \rho U_\infty^2 A}$$

### Pressure Coefficient

$$C_p = \frac{p - p_\infty}{0.5 \rho U_\infty^2}$$

### Strouhal Number (Vortex Shedding)

$$St = \frac{f_s D}{U_\infty} \approx 0.2 \quad \text{(cylinder)}$$

---

## 2. Domain Sizing

| Direction | Size |
|-----------|------|
| Upstream | 5-10L |
| Downstream | 15-20L |
| Side/Top | 5-10L |

---

## 3. Mesh Settings

### snappyHexMeshDict

```cpp
refinementSurfaces
{
    vehicle
    {
        level (2 2);
        patchInfo { type wall; }
    }
}

refinementRegions
{
    wakeBox
    {
        mode inside;
        levels ((10 2) (20 3));
    }
}

addLayersControls
{
    layers
    {
        vehicle
        {
            nSurfaceLayers      15;
            expansionRatio      1.2;
            finalLayerThickness 0.5;
        }
    }
}
```

### $y^+$ Guidelines

| Approach | $y^+$ | Layers |
|----------|-------|--------|
| Wall-resolved | ≈ 1 | 10-15 |
| Wall functions | 30-300 | 5-10 |

---

## 4. Force Calculation

### Function Object

```cpp
// system/controlDict
functions
{
    forcesCoeffs
    {
        type        forces;
        libs        (fieldFunctionObjects);
        patches     (vehicleBody);
        
        rho         rhoInf;
        rhoInf      1.225;
        
        dragDir     (1 0 0);
        liftDir     (0 0 1);
        
        magUInf     30.0;
        lRef        4.5;
        Aref        2.2;
    }
}
```

**Output:** `postProcessing/forcesCoeffs/0/forceCoeffs.dat`

---

## 5. Turbulence Model

### k-ω SST (Recommended)

```cpp
// constant/turbulenceProperties
simulationType RAS;

RAS
{
    RASModel    kOmegaSST;
    turbulence  on;
}
```

### Model Selection

| Model | Accuracy | Cost | Use |
|-------|----------|------|-----|
| k-ω SST | High | Medium | Attached + mild separation |
| k-ε | Medium | Low | Free shear |
| DES | High | High | Massive separation |

---

## 6. Boundary Conditions

### Inlet

```cpp
// 0/U
inlet
{
    type            freestreamVelocity;
    freestreamValue uniform (30 0 0);
}

// 0/k
inlet
{
    type    fixedValue;
    value   uniform 0.24;  // k = 1.5*(U*I)², I=0.5%
}
```

### Wall

```cpp
// 0/U
vehicle { type noSlip; }

// 0/k
vehicle { type kLowReWallFunction; value uniform 0; }

// 0/omega
vehicle { type omegaWallFunction; value uniform 0; }
```

---

## 7. Solver Settings

### Steady (simpleFoam)

```cpp
SIMPLE
{
    nNonOrthogonalCorrectors 2;
    residualControl { p 1e-6; U 1e-6; }
}

relaxationFactors
{
    fields    { p 0.3; }
    equations { U 0.7; k 0.7; omega 0.7; }
}
```

### Transient (pimpleFoam)

```cpp
PIMPLE
{
    nCorrectors 2;
    nNonOrthogonalCorrectors 2;
}

adjustTimeStep yes;
maxCo          0.8;
```

---

## 8. Post-Processing

### Wake Analysis

```cpp
functions
{
    wakeAnalysis
    {
        type    sets;
        sets
        (
            wakeLineX
            {
                type    uniform;
                axis    x;
                start   (3 0 0);
                end     (10 0 0);
                nPoints 100;
            }
        );
        fields  (p U k);
    }
}
```

### Drag Decomposition

$$C_D = C_{D,pressure} + C_{D,friction}$$

---

## Concept Check

<details>
<summary><b>1. ทำไม downstream ต้องยาวกว่า upstream?</b></summary>

Wake ขยายตัวไปด้านหลัง — ต้องมีพื้นที่พอให้ pressure recover ก่อนชน outlet boundary มิฉะนั้น BC จะส่งผลกลับมาที่ flow รอบวัตถุ
</details>

<details>
<summary><b>2. k-ω SST ดีกว่า k-ε ตรงไหน?</b></summary>

SST ใช้ k-ω ใกล้ผนัง (ไวต่อ adverse pressure gradient) และ k-ε ไกลผนัง (robust ใน free stream) → ทำนาย flow separation ได้ดีกว่า
</details>

<details>
<summary><b>3. ทำไม Pressure Drag มักใหญ่กว่า Friction Drag?</b></summary>

สำหรับ bluff bodies ส่วนใหญ่ Pressure Drag มาจาก wake (low pressure behind) ซึ่ง dominant กว่า skin friction — streamlined bodies จะกลับกัน
</details>

---

## Related Documents

- **บทถัดไป:** [02_Internal_Flow_and_Piping.md](02_Internal_Flow_and_Piping.md)
- **Turbulence:** [../03_TURBULENCE_MODELING/00_Overview.md](../03_TURBULENCE_MODELING/00_Overview.md)