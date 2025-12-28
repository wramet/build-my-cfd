# Turbulence Modeling Overview

ภาพรวมการสร้างแบบจำลองความปั่นป่วนใน OpenFOAM

---

## ทำไมต้องเรียนโมดูลนี้?

การเลือก Turbulence Model ที่เหมาะสมกำหนด:
- **ความแม่นยำ** — RANS vs LES vs DNS
- **ความเสถียร** — Wall treatment ที่ถูกต้อง
- **ต้นทุน** — ชั่วโมงคำนวณ vs ความละเอียด

---

## Simulation Types

| Type | Resolved | Modeled | Cost | Use Case |
|------|----------|---------|------|----------|
| **RANS** | Mean flow | All turbulence | Low | Industrial |
| **LES** | Large eddies | Small eddies | High | Research |
| **DNS** | All scales | None | Highest | Fundamental |

```cpp
// constant/turbulenceProperties
simulationType  RAS;     // หรือ LES, DNS

RAS
{
    RASModel    kOmegaSST;
    turbulence  on;
}
```

---

## RANS Models

### Model Selection

| Model | Best For | $y^+$ |
|-------|----------|-------|
| `kEpsilon` | Free-shear, far from walls | 30-300 |
| `kOmegaSST` | Wall-bounded, separation | 1 or 30-300 |
| `SpalartAllmaras` | External aero | 1 or 30-300 |
| `realizableKE` | Strong vortices | 30-300 |

### Boussinesq Hypothesis

$$\tau_{ij} = 2\mu_t S_{ij} - \frac{2}{3}\rho k \delta_{ij}$$

### k-ω SST (Recommended)

```cpp
RAS
{
    RASModel        kOmegaSST;
    turbulence      on;
    printCoeffs     on;
}
```

**Fields required:** `0/k`, `0/omega`, `0/nut`

---

## LES Models

### SGS Models

| Model | Characteristics |
|-------|-----------------|
| `Smagorinsky` | Simple, stable |
| `WALE` | Good wall behavior |
| `dynamicSmagorinsky` | Auto-tuning |
| `oneEqEddy` | k-equation |

```cpp
simulationType  LES;

LES
{
    LESModel    Smagorinsky;
    delta       cubeRootVol;
    
    SmagorinskyCoeffs { Cs 0.1; }
}
```

---

## Wall Treatment

### $y^+$ Definition

$$y^+ = \frac{y u_\tau}{\nu}, \quad u_\tau = \sqrt{\frac{\tau_w}{\rho}}$$

### Strategy Selection

| Approach | $y^+$ Target | Wall Functions |
|----------|--------------|----------------|
| Wall-resolved | ≈ 1 | `nutLowReWallFunction` |
| Wall-modeled | 30-300 | `nutkWallFunction` |

### Boundary Conditions

```cpp
// 0/nut - High-Re
walls
{
    type    nutkWallFunction;
    value   uniform 0;
}

// 0/k
walls
{
    type    kqRWallFunction;
    value   uniform 0;
}

// 0/epsilon
walls
{
    type    epsilonWallFunction;
    value   uniform 0;
}

// 0/omega
walls
{
    type    omegaWallFunction;
    value   uniform 0;
}
```

---

## Inlet Conditions

### From Turbulence Intensity

$$k = \frac{3}{2}(U \cdot I)^2$$
$$\epsilon = C_\mu^{0.75} \frac{k^{1.5}}{l}$$
$$\omega = \frac{\sqrt{k}}{C_\mu^{0.25} l}$$

- $I$ = turbulence intensity (typically 0.01 - 0.1)
- $l$ = mixing length (typically 0.07 × hydraulic diameter)

```cpp
// 0/k
inlet
{
    type        turbulentIntensityKineticEnergyInlet;
    intensity   0.05;
    value       uniform 1;
}

// 0/epsilon
inlet
{
    type        turbulentMixingLengthDissipationRateInlet;
    mixingLength 0.01;
    value       uniform 1;
}
```

---

## Check $y^+$

```bash
# After simulation
postProcess -func yPlus

# Or add to controlDict
functions
{
    yPlus
    {
        type    yPlus;
        libs    (fieldFunctionObjects);
    }
}
```

---

## Quick Reference

### Files Modified

| File | Purpose |
|------|---------|
| `constant/turbulenceProperties` | Model selection |
| `0/k` | TKE field |
| `0/epsilon` or `0/omega` | Dissipation |
| `0/nut` | Turbulent viscosity |

### Typical Workflow

```bash
# 1. Choose model in turbulenceProperties
# 2. Set inlet k, epsilon/omega from intensity
# 3. Set wall functions based on y+ target
# 4. Run and check y+
# 5. Adjust mesh if y+ out of range
```

---

## Concept Check

<details>
<summary><b>1. k-ε กับ k-ω SST ต่างกันอย่างไร?</b></summary>

- **k-ε:** ดีสำหรับ free-shear flows แต่ต้องใช้ wall functions
- **k-ω SST:** รวมข้อดีของทั้งคู่ — k-ω ใกล้ผนัง, k-ε ห่างจากผนัง → แนะนำสำหรับงานทั่วไป
</details>

<details>
<summary><b>2. $y^+$ ควรอยู่ในช่วงไหน?</b></summary>

- **Wall-resolved:** $y^+ \approx 1$ (ใช้ Low-Re model หรือ LES)
- **Wall functions:** $y^+ = 30-300$ (หลีกเลี่ยง buffer layer 5-30)
</details>

<details>
<summary><b>3. ทำไม SST ถึงนิยม?</b></summary>

SST (Shear Stress Transport) ใช้ blending function เพื่อเลือก k-ω ใกล้ผนังและ k-ε ห่างจากผนังอัตโนมัติ — ทำนาย flow separation ได้ดีกว่า k-ε มาตรฐาน
</details>

---

## Learning Path

```mermaid
flowchart LR
    A[00_Overview] --> B[01_RANS_Models]
    B --> C[02_Advanced_Turbulence]
    C --> D[03_Wall_Treatment]
    D --> E[04_LES_Fundamentals]
```

---

## Related Documents

- **บทถัดไป:** [01_RANS_Models.md](01_RANS_Models.md)
- **Wall Treatment:** [03_Wall_Treatment.md](03_Wall_Treatment.md)