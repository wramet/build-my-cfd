# Advanced Turbulence Models

LES, DES, Transition modeling สำหรับการไหลที่ RANS ไม่เพียงพอ

---

## เมื่อไหร่ควรใช้ Advanced Models?

| สถานการณ์ | RANS | LES | DES |
|-----------|------|-----|-----|
| Steady attached flow | ✅ | ❌ | ❌ |
| Vortex shedding | ❌ | ✅ | ✅ |
| Massive separation | ❌ | ✅ | ✅ |
| Swirling flow | ⚠️ | ✅ | ✅ |
| High Re + wall | ❌ | ❌ | ✅ |

---

## 1. Large Eddy Simulation (LES)

### หลักการ

Resolve large eddies + Model small eddies (SGS)

**Filtered N-S:**
$$\frac{\partial \bar{u}_i}{\partial t} + \bar{u}_j\frac{\partial \bar{u}_i}{\partial x_j} = -\frac{1}{\rho}\frac{\partial \bar{p}}{\partial x_i} + \nu\frac{\partial^2 \bar{u}_i}{\partial x_j^2} - \frac{\partial \tau_{ij}}{\partial x_j}$$

**Smagorinsky SGS:**
$$\nu_t = (C_s \Delta)^2 |\bar{S}|$$

### SGS Models

| Model | Use Case | Cs |
|-------|----------|-----|
| Smagorinsky | General | 0.1-0.2 |
| dynamicKEqn | Complex flows | Dynamic |
| WALE | Wall-bounded | — |
| kEqn | Unsteady | — |

### OpenFOAM Setup

```cpp
// constant/turbulenceProperties
simulationType LES;

LES
{
    LESModel        Smagorinsky;
    turbulence      on;
    delta           cubeRootVol;
    
    SmagorinskyCoeffs
    {
        Cs          0.1;
    }
}
```

### Requirements

| Parameter | Requirement |
|-----------|-------------|
| y+ | ≈ 1 (wall-resolved) |
| Δx+ | 50-100 |
| Δz+ | 15-30 |
| CFL | 0.3-0.5 |
| Aspect ratio | ≈ 1 (isotropic) |

```cpp
// system/controlDict
maxCo   0.5;
```

---

## 2. Detached Eddy Simulation (DES)

### หลักการ

Hybrid = RANS (near wall) + LES (separated regions)

$$l_{DES} = \min(l_{RANS}, C_{DES} \Delta)$$

### Variants

| Type | Feature | Use |
|------|---------|-----|
| DES | Basic switching | May cause GIS |
| DDES | Delay function | Prevents early switch |
| IDDES | Improved blending | Best transition |

### OpenFOAM Setup

```cpp
// constant/turbulenceProperties
simulationType DES;

DES
{
    DESModel        SpalartAllmarasIDDES;
    turbulence      on;
    CDES            0.65;
}
```

### Mesh Requirements

| Zone | y+ |
|------|-----|
| RANS (near wall) | 30-100 |
| LES (separated) | Refined, isotropic |
| Transition | Gradual change |

**⚠️ Avoid Grid-Induced Separation:** Don't refine too much in RANS zone

---

## 3. Transition Modeling

### Mechanisms

| Type | Trigger | Application |
|------|---------|-------------|
| Natural | T-S waves | Low disturbance BL |
| Bypass | High Tu (>1%) | Turbomachinery |
| Separation-induced | Laminar bubble | Low Re airfoils |

### γ-Reθ Model

- **γ (Intermittency):** 0 = laminar, 1 = turbulent
- **Reθ:** Momentum thickness Reynolds number

```cpp
// constant/turbulenceProperties
simulationType RAS;

RAS
{
    RASModel        kOmegaSST;
    turbulence      on;
    transition      on;
    transitionModel gammaReTheta;
    
    gammaReThetaCoeffs
    {
        maxTransitionLength 50;
        criticalReThet      200;
    }
}
```

**Additional fields:**
- `0/gamma` — Intermittency
- `0/ReTheta` — Transition Re
- `0/thetat` — Momentum thickness Re

---

## 4. Computational Cost

| Method | Cost | Accuracy |
|--------|------|----------|
| RANS | 1× | Basic |
| DES | 5-20× | Good |
| LES | 100× | Excellent |
| DNS | 10000× | Exact |

---

## Quick Reference

### LES Workflow

```bash
# 1. Create fine, isotropic mesh (y+ ≈ 1)
blockMesh / snappyHexMesh
checkMesh  # Check quality

# 2. Set turbulenceProperties
simulationType LES;
LESModel Smagorinsky;

# 3. Set maxCo
maxCo 0.5;

# 4. Run with pimpleFoam
pimpleFoam
```

### DES Workflow

```bash
# 1. Create hybrid mesh (y+ ≈ 30 near wall)
# 2. Set turbulenceProperties
simulationType DES;
DESModel SpalartAllmarasIDDES;

# 3. Run
pimpleFoam
```

---

## Concept Check

<details>
<summary><b>1. LES กับ DES ต่างกันอย่างไร?</b></summary>

- **LES**: Resolve eddies ทั้งหมด ต้องการ y+ ≈ 1
- **DES**: ใช้ RANS ใกล้ผนัง (y+ ≈ 30) + LES ใน separated region → ประหยัดกว่า
</details>

<details>
<summary><b>2. DDES กับ DES ต่างกันอย่างไร?</b></summary>

DDES มี "delay function" ป้องกันการ switch จาก RANS เป็น LES เร็วเกินไป ซึ่งป้องกัน Grid-Induced Separation
</details>

<details>
<summary><b>3. γ-Reθ model ใช้ทำอะไร?</b></summary>

ใช้ทำนาย transition จาก laminar → turbulent โดย γ (intermittency) = 0 → 1 ระหว่าง transition region
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_High_Performance_Computing.md](01_High_Performance_Computing.md)
- **บทถัดไป:** [03_Numerical_Methods.md](03_Numerical_Methods.md)