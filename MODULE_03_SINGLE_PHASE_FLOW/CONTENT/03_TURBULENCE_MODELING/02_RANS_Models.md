# RANS Models

Reynolds-Averaged Navier-Stokes Turbulence Models

---

## Overview

RANS models แก้สมการ **time-averaged** แทน instantaneous → ลด cost จากวันเหลือชั่วโมง

**Core Concept:** Reynolds decomposition

$$\phi = \overline{\phi} + \phi'$$

---

## 1. k-ε Model

### Transport Equations

**Turbulent Kinetic Energy:**
$$\frac{\partial k}{\partial t} + \nabla \cdot (\mathbf{u}k) = \nabla \cdot \left[\left(\nu + \frac{\nu_t}{\sigma_k}\right)\nabla k\right] + G - \varepsilon$$

**Dissipation Rate:**
$$\frac{\partial \varepsilon}{\partial t} + \nabla \cdot (\mathbf{u}\varepsilon) = \nabla \cdot \left[\left(\nu + \frac{\nu_t}{\sigma_\varepsilon}\right)\nabla \varepsilon\right] + C_1\frac{\varepsilon}{k}G - C_2\frac{\varepsilon^2}{k}$$

### Eddy Viscosity

$$\nu_t = C_\mu \frac{k^2}{\varepsilon}$$

### Standard Coefficients

| Constant | Value |
|----------|-------|
| $C_\mu$ | 0.09 |
| $C_1$ | 1.44 |
| $C_2$ | 1.92 |
| $\sigma_k$ | 1.0 |
| $\sigma_\varepsilon$ | 1.3 |

### Pros/Cons

✅ Stable, fast convergence, good for free-shear  
❌ Poor near-wall, under-predicts separation

---

## 2. k-ω SST Model

### Blending Function

SST ใช้ $F_1$ เพื่อสลับ:
- Near wall ($F_1 \to 1$): k-ω behavior
- Free stream ($F_1 \to 0$): k-ε behavior

### Eddy Viscosity Limiter

$$\nu_t = \frac{a_1 k}{\max(a_1\omega, SF_2)}$$

ป้องกัน over-prediction ใน separation zones

### SST Coefficients

| Constant | Inner | Outer |
|----------|-------|-------|
| $\alpha_k$ | 0.85 | 1.0 |
| $\alpha_\omega$ | 0.5 | 0.856 |
| $\beta$ | 0.075 | 0.0828 |
| $\beta^*$ | 0.09 | 0.09 |
| $a_1$ | 0.31 | 0.31 |

### Pros/Cons

✅ Excellent near-wall, good separation prediction  
❌ Higher cost, more sensitive to mesh

---

## 3. OpenFOAM Setup

### turbulenceProperties

```cpp
simulationType RAS;

RAS
{
    RASModel    kOmegaSST;  // or kEpsilon
    turbulence  on;
    printCoeffs on;
}
```

### Initial/Boundary Conditions

**From Intensity and Length Scale:**

$$k = \frac{3}{2}(UI)^2, \quad \varepsilon = C_\mu^{3/4}\frac{k^{3/2}}{L_t}$$

```cpp
// 0/k
inlet
{
    type    turbulentIntensityKineticEnergyInlet;
    intensity 0.05;  // 5%
    value   uniform 0.01;
}

// 0/epsilon
inlet
{
    type    turbulentMixingLengthDissipationRateInlet;
    mixingLength 0.01;  // [m]
    value   uniform 0.01;
}
```

### Wall Boundary Conditions

```cpp
// 0/k
wall { type kLowReWallFunction; value uniform 0; }

// 0/epsilon
wall { type epsilonWallFunction; value uniform 0; }

// 0/omega
wall { type omegaWallFunction; value uniform 0; }

// 0/nut
wall { type nutkWallFunction; value uniform 0; }
```

---

## 4. Model Selection

| Flow Type | k-ε | k-ω SST |
|-----------|-----|---------|
| Internal (pipe) | ✓ | ✓ |
| External (airfoil) | ✗ | ✓ |
| Separation | ✗ | ✓ |
| Adverse pressure gradient | ✗ | ✓ |
| Fast computation | ✓ | ✗ |

### Recommendation

- **Default choice:** k-ω SST
- **Simple internal flow:** k-ε acceptable
- **Separation/external:** k-ω SST mandatory

---

## 5. $y^+$ Requirements

| Approach | $y^+$ | Wall BC |
|----------|-------|---------|
| Wall functions | 30-300 | `*WallFunction` |
| Low-Re (resolve) | ≈ 1 | `kLowReWallFunction` |

```bash
postProcess -func yPlus
```

---

## Concept Check

<details>
<summary><b>1. k-ε ทำไมทำนาย separation แย่?</b></summary>

เพราะ k-ε มักจะ **over-predict $\nu_t$** ใกล้ผนัง → flow เกาะผิวได้ดีเกินจริง → delay separation
</details>

<details>
<summary><b>2. SST "blend" ระหว่าง k-ω และ k-ε อย่างไร?</b></summary>

ใช้ **blending function $F_1$**:
- ใกล้ผนัง: $F_1 \to 1$ → k-ω (ดีสำหรับ boundary layer)
- ไกลผนัง: $F_1 \to 0$ → k-ε (เสถียรใน free stream)
</details>

<details>
<summary><b>3. $y^+ = 1$ จำเป็นเสมอไหม?</b></summary>

**ไม่** — ขึ้นกับ approach:
- Low-Re (resolve viscous sublayer): $y^+ \approx 1$
- Wall functions: $y^+ = 30-300$
</details>

---

## Related Documents

- **บทก่อนหน้า:** [01_Turbulence_Fundamentals.md](01_Turbulence_Fundamentals.md)
- **บทถัดไป:** [03_Wall_Treatment.md](03_Wall_Treatment.md)