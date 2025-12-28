# Benchmark Problems สำหรับ Multiphase Flow

ปัญหาเบนช์มาร์กมาตรฐานสำหรับการตรวจสอบความถูกต้อง

---

## Overview

```mermaid
flowchart LR
    A[Code Verification] --> B[Solution Verification]
    B --> C[Model Validation]
    C --> D[Prediction]
```

| ระดับ | เป้าหมาย | วิธีการ |
|-------|---------|---------|
| Code Verification | Math ถูกต้อง? | Exact solutions |
| Solution Verification | Discretization error? | Grid convergence |
| Model Validation | Physics ถูกต้อง? | Experimental data |

---

## 1. Single Bubble Rising

### Physical Setup

| Parameter | Value |
|-----------|-------|
| Diameter | 2-10 mm |
| Domain | 10 × $d_b$ |
| Solver | `interFoam` |

### Dimensionless Numbers

$$Eo = \frac{g(\rho_l - \rho_g)d_b^2}{\sigma}$$

$$Re_b = \frac{\rho_l u_t d_b}{\mu_l}$$

$$Mo = \frac{g\mu_l^4(\rho_l - \rho_g)}{\rho_l^2 \sigma^3}$$

### OpenFOAM Setup

```cpp
// constant/transportProperties
phases (gas liquid);

liquid
{
    transportModel  Newtonian;
    nu   [0 2 -1 0 0 0 0] 1.0e-6;
    rho  [1 -3 0 0 0 0 0] 1000;
}

gas
{
    transportModel  Newtonian;
    nu   [0 2 -1 0 0 0 0] 1.5e-5;
    rho  [1 -3 0 0 0 0 0] 1.2;
}

sigma  [1 0 -2 0 0 0 0] 0.072;
```

### Acceptance Criteria

| Metric | Target |
|--------|--------|
| Velocity error | < 10% (spherical), < 15% (deformed) |
| Volume conservation | < 2% |

---

## 2. Stratified Two-Phase Flow

### Physical Setup

| Parameter | Value |
|-----------|-------|
| Pipe diameter | 0.05 m |
| Length | 10D |
| $U_{gas}$ | 1-10 m/s |
| $U_{liquid}$ | 0.1-1 m/s |

### Dimensionless Numbers

$$Fr = \frac{U_g}{\sqrt{gD}}$$

$$X = \sqrt{\frac{(dP/dx)_l}{(dP/dx)_g}}$$

### Validation Metrics

| Metric | Correlation |
|--------|-------------|
| Liquid height | Taitel-Dukler |
| Pressure drop | Lockhart-Martinelli |

---

## 3. Fluidized Bed

### Physical Setup

| Parameter | Value |
|-----------|-------|
| Bed dimensions | 0.3 × 0.3 × 2.0 m |
| Particle diameter | 500 μm |
| Particle density | 2500 kg/m³ |
| Solver | `multiphaseEulerFoam` |

### Operating Regimes

| Regime | Velocity |
|--------|----------|
| Minimum fluidization | $U_{mf}$ |
| Bubbling | 1.5-3.0 × $U_{mf}$ |
| Transport | > 5 × $U_{mf}$ |

### Key Correlations

**Ergun Equation (packed bed):**
$$\frac{\Delta P}{L} = \frac{150\mu(1-\varepsilon)^2}{\varepsilon^3 d_p^2}U + \frac{1.75\rho(1-\varepsilon)}{\varepsilon^3 d_p}U^2$$

### OpenFOAM Setup

```cpp
// constant/phaseProperties
phases (particles air);

particles
{
    diameterModel constant;
    d   0.0005;
    alphaMax 0.63;
}

drag
{
    (particles in air)
    {
        type GidaspowErgunWenYu;
    }
}
```

---

## 4. Bubble Column

### Physical Setup

| Parameter | Value |
|-----------|-------|
| Height | 1-2 m |
| Diameter | 0.15-0.3 m |
| Gas holdup | 5-30% |
| Solver | `multiphaseEulerFoam` |

### Validation Metrics

| Quantity | Measurement |
|----------|-------------|
| Gas holdup | Conductivity probe |
| Bubble size | Image analysis |
| Velocity | PIV/LDA |

---

## 5. OpenFOAM Validation Tools

### Function Objects

```cpp
// system/controlDict
functions
{
    bubbleTrack
    {
        type            volRegion;
        operation       volAverage;
        fields          (alpha.gas);
        writeControl    timeStep;
    }

    probes
    {
        type            probes;
        probeLocations  ((0.05 0.1 0.5) (0.05 0.1 1.0));
        fields          (U p alpha.gas);
    }
}
```

### Post-Processing

```bash
# Sample along line
postProcess -func sample

# Extract gas holdup
postProcess -func "volRegion(name=liquid)"
```

---

## Quick Reference

| Benchmark | Physics | Solver | Key Metric |
|-----------|---------|--------|------------|
| Bubble rising | Surface tension | `interFoam` | Terminal velocity |
| Stratified | Gravity separation | `interFoam` | Liquid height |
| Fluidized bed | Gas-solid drag | `multiphaseEulerFoam` | Bed expansion |
| Bubble column | Bubble dynamics | `multiphaseEulerFoam` | Gas holdup |

---

## Concept Check

<details>
<summary><b>1. ทำไม benchmark cases ถึงสำคัญ?</b></summary>

Benchmarks ช่วยให้เรา **มั่นใจ** ว่า:
- Code implementation ถูกต้อง
- Discretization error อยู่ในระดับที่ยอมรับได้
- Physics models ทำนายปรากฏการณ์จริงได้ถูกต้อง
</details>

<details>
<summary><b>2. Eo, Mo, Re บอกอะไรเกี่ยวกับ bubble behavior?</b></summary>

- **Eo (Eötvös)**: buoyancy vs surface tension → รูปทรงฟอง
- **Mo (Morton)**: fluid properties → ระบบการไหล
- **Re (Reynolds)**: inertia vs viscosity → laminar/turbulent wake
</details>

<details>
<summary><b>3. ทำไม fluidized bed ต้องใช้ Eulerian solver?</b></summary>

เพราะมี **high particle concentration** ที่ particles โต้ตอบกันบ่อย — Lagrangian tracking ไม่เหมาะสำหรับ dense systems
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Validation Methodology:** [01_Validation_Methodology.md](01_Validation_Methodology.md)
- **Grid Convergence:** [03_Grid_Convergence.md](03_Grid_Convergence.md)