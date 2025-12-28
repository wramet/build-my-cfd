# Internal Flow and Piping

การจำลองการไหลในท่อและระบบท่อ

---

## Overview

| Parameter | Formula | Use |
|-----------|---------|-----|
| Reynolds number | $Re = \frac{\rho U D}{\mu}$ | Flow regime |
| Pressure drop | $\Delta p = f \frac{L}{D} \frac{\rho U^2}{2}$ | Pump sizing |
| Friction factor | $f = 64/Re$ (laminar) | Energy loss |

---

## 1. Flow Regimes

| $Re$ Range | Regime | Velocity Profile |
|------------|--------|------------------|
| < 2300 | Laminar | Parabolic |
| 2300-4000 | Transitional | Unstable |
| > 4000 | Turbulent | Plug-like |

### Laminar Profile

$$u(r) = 2U_{avg}\left[1 - \left(\frac{r}{R}\right)^2\right]$$

### Law of the Wall (Turbulent)

$$u^+ = \frac{1}{\kappa}\ln y^+ + C$$

---

## 2. Pressure Drop

### Darcy-Weisbach Equation

$$\Delta p = f \frac{L}{D} \frac{\rho U^2}{2}$$

### Friction Factor

| Flow | Formula |
|------|---------|
| Laminar | $f = 64/Re$ |
| Turbulent | Colebrook-White: $\frac{1}{\sqrt{f}} = -2\log\left(\frac{\epsilon/D}{3.7} + \frac{2.51}{Re\sqrt{f}}\right)$ |

### Minor Losses

| Fitting | $K$ |
|---------|-----|
| 90° smooth elbow | 0.2-0.3 |
| 90° sharp elbow | 1.1 |
| Tee junction | 1.8 |

---

## 3. OpenFOAM Setup

### Solver Selection

| Solver | Use Case |
|--------|----------|
| `simpleFoam` | Steady-state |
| `pimpleFoam` | Transient |
| `buoyantSimpleFoam` | Heat transfer |

### Boundary Conditions

**0/U:**
```cpp
inlet  { type fixedValue; value uniform (1 0 0); }
outlet { type zeroGradient; }
walls  { type noSlip; }
```

**0/p:**
```cpp
inlet  { type zeroGradient; }
outlet { type fixedValue; value uniform 0; }
walls  { type zeroGradient; }
```

---

## 4. Entry Length

การไหลต้องการระยะทางพัฒนาตัว:

| Flow | Entry Length |
|------|--------------|
| Laminar | $L_e \approx 0.06 D Re$ |
| Turbulent | $L_e \approx 4.4 D Re^{1/6}$ |

> ถ้าท่อสั้นกว่า $L_e$ ให้ใช้ fully-developed profile ที่ inlet

---

## 5. Function Objects

### Pressure Drop

```cpp
pInlet
{
    type    surfaceFieldValue;
    operation weightedAverage;
    weightField phi;
    patches (inlet);
    fields  (p);
}
```

### Wall Shear Stress

```cpp
wallShearStress
{
    type    wallShearStress;
    patches (walls);
}
```

### Forces

```cpp
forces
{
    type    forces;
    patches (walls);
    rhoInf  1000;
    CofR    (0 0 0);
}
```

---

## 6. Mesh Guidelines

| Criterion | Target |
|-----------|--------|
| Orthogonality | > 60° |
| Aspect ratio | < 1000 |
| Skewness | < 0.85 |
| $y^+$ (wall function) | 30-300 |

### Boundary Layer

```cpp
// snappyHexMeshDict
addLayers
{
    walls
    {
        nSurfaceLayers 10;
        expansionRatio 1.2;
        finalLayerThickness 0.001;
    }
}
```

---

## 7. Heat Transfer (Dittus-Boelter)

$$Nu = 0.023 Re^{0.8} Pr^{0.4}$$

$$h = \frac{Nu \cdot k}{D}$$

---

## Concept Check

<details>
<summary><b>1. ทำไม $\Delta p \propto U^2$ ในช่วง Turbulent?</b></summary>

เพราะใน turbulent flow แรงต้านหลักมาจาก **inertial forces** (ไม่ใช่ viscous) — inertia สัมพันธ์กับ kinetic energy ($\frac{1}{2}\rho U^2$)
</details>

<details>
<summary><b>2. Entry length สำคัญอย่างไร?</b></summary>

ถ้าท่อสั้นกว่า entry length การใช้สูตร friction factor มาตรฐานจะผิด เพราะ wall shear stress ในช่วง developing flow สูงกว่าปกติ
</details>

<details>
<summary><b>3. `zeroGradient` ที่ outlet หมายความว่าอย่างไร?</b></summary>

หมายความว่า $\frac{\partial \phi}{\partial n} = 0$ — field ไม่เปลี่ยนแปลงในทิศทางตั้งฉากกับ boundary ใช้สำหรับ fully-developed outflow
</details>

---

## Related Documents

- **บทก่อนหน้า:** [01_External_Aerodynamics.md](01_External_Aerodynamics.md)
- **บทถัดไป:** [03_Heat_Exchangers.md](03_Heat_Exchangers.md)