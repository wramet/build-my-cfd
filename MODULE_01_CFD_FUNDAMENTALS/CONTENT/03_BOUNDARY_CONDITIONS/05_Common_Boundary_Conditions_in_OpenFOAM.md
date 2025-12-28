# Common Boundary Conditions in OpenFOAM

รายละเอียดของ BC ที่ใช้บ่อยพร้อม code examples

---

## Velocity BCs

### fixedValue

กำหนดค่าความเร็วโดยตรง

```cpp
inlet
{
    type    fixedValue;
    value   uniform (10 0 0);   // m/s
}
```

### noSlip

Shorthand สำหรับ fixedValue (0 0 0)

```cpp
wall { type noSlip; }
```

### slip

ไม่มี shear stress, ความเร็ว normal = 0

```cpp
symmetryWall { type slip; }
```

### zeroGradient

Extrapolate จาก internal field

```cpp
outlet { type zeroGradient; }
```

### inletOutlet

จัดการ backflow อัตโนมัติ

```cpp
outlet
{
    type        inletOutlet;
    inletValue  uniform (0 0 0);    // ใช้ถ้า flow กลับ
    value       uniform (10 0 0);   // initial
}
```

### pressureInletVelocity

คำนวณ U จาก pressure gradient

```cpp
inlet
{
    type    pressureInletVelocity;
    value   uniform (0 0 0);    // initial guess
}
```

### freestreamVelocity

Far-field สำหรับ external flow

```cpp
farField
{
    type            freestreamVelocity;
    freestreamValue uniform (50 0 0);
}
```

### movingWallVelocity

ผนังเคลื่อนที่

```cpp
belt
{
    type    movingWallVelocity;
    value   uniform (1 0 0);
}
```

---

## Pressure BCs

### fixedValue

กำหนดความดัน (gauge หรือ absolute)

```cpp
outlet
{
    type    fixedValue;
    value   uniform 0;      // Pa (gauge)
}
```

### zeroGradient

ปล่อยให้ p ปรับตัวตามธรรมชาติ

```cpp
inlet { type zeroGradient; }
wall  { type zeroGradient; }
```

### totalPressure

กำหนด total pressure (รวม dynamic head)

```cpp
inlet
{
    type    totalPressure;
    p0      uniform 10000;  // Pa
    gamma   1.4;            // สำหรับ compressible
}
```

### freestreamPressure

Far-field pressure

```cpp
farField
{
    type            freestreamPressure;
    freestreamValue uniform 0;
}
```

### fixedFluxPressure

รักษา mass flux ที่กำหนด

```cpp
wall
{
    type    fixedFluxPressure;
    value   uniform 0;
}
```

---

## Temperature BCs

### fixedValue

อุณหภูมิคงที่

```cpp
hotWall
{
    type    fixedValue;
    value   uniform 400;    // K
}
```

### zeroGradient

ผนัง adiabatic

```cpp
insulated { type zeroGradient; }
```

### fixedGradient

Heat flux คงที่

```cpp
heatedWall
{
    type        fixedGradient;
    gradient    uniform 1000;   // K/m (= q''/k)
}
```

### externalWallHeatFlux

Convective/radiative heat transfer

```cpp
// Coefficient mode (Newton's cooling)
convWall
{
    type    externalWallHeatFlux;
    mode    coefficient;
    h       uniform 10;     // W/(m²·K)
    Ta      uniform 300;    // K
}

// Power mode (fixed total heat)
heater
{
    type    externalWallHeatFlux;
    mode    power;
    Q       100;            // W total
}

// Flux mode
fluxWall
{
    type    externalWallHeatFlux;
    mode    flux;
    q       uniform 5000;   // W/m²
}
```

---

## Turbulence BCs

### At Inlet

```cpp
// k (turbulent kinetic energy)
inlet
{
    type    fixedValue;
    value   uniform 0.1;    // m²/s²
}

// epsilon (dissipation rate)
inlet
{
    type    fixedValue;
    value   uniform 0.01;   // m²/s³
}

// omega (specific dissipation)
inlet
{
    type    fixedValue;
    value   uniform 100;    // 1/s
}

// nut (turbulent viscosity)
inlet
{
    type    calculated;
    value   uniform 0;
}
```

### At Wall (Wall Functions)

```cpp
// k
wall { type kqRWallFunction; value uniform 0.1; }

// epsilon
wall { type epsilonWallFunction; value uniform 0.01; }

// omega
wall { type omegaWallFunction; value uniform 100; }

// nut
wall
{
    type    nutkWallFunction;
    value   uniform 0;
    Cmu     0.09;
    kappa   0.41;
    E       9.8;
}
```

### At Outlet

```cpp
// ทุก turbulence field
outlet { type zeroGradient; }
```

---

## Special BCs

### symmetry

สมมาตร

```cpp
symmetryPlane { type symmetry; }
```

### cyclic

Periodic boundary (ต้องกำหนดใน polyMesh/boundary ด้วย)

```cpp
left  { type cyclic; }
right { type cyclic; }
```

### empty

2D simulation (ไม่มี flux ในทิศทางนั้น)

```cpp
frontAndBack { type empty; }
```

### wedge

Axisymmetric simulation

```cpp
wedgeFront { type wedge; }
wedgeBack  { type wedge; }
```

---

## BC Estimation Formulas

### Turbulent Intensity

$$I = \frac{u'}{U} \approx 0.01 - 0.10$$

### Turbulent Kinetic Energy

$$k = \frac{3}{2}(U \cdot I)^2$$

### Dissipation Rate (epsilon)

$$\varepsilon = C_\mu^{3/4} \frac{k^{3/2}}{l}$$

โดย $l \approx 0.07 D$ (hydraulic diameter)

### Specific Dissipation (omega)

$$\omega = \frac{\varepsilon}{C_\mu k}$$

---

## Concept Check

<details>
<summary><b>1. inletOutlet กับ pressureInletOutletVelocity ต่างกันอย่างไร?</b></summary>

- `inletOutlet`: ใช้ inletValue ถ้า flow reverse
- `pressureInletOutletVelocity`: คำนวณ U จาก pressure ถ้า flow reverse
</details>

<details>
<summary><b>2. totalPressure ใช้เมื่อไหร่?</b></summary>

เมื่อต้องการรักษา stagnation pressure คงที่ (เช่น inlet ที่มี varying velocity) โดย $p_0 = p + \frac{1}{2}\rho|U|^2$
</details>

<details>
<summary><b>3. ทำไม nut ใช้ calculated ที่ inlet?</b></summary>

เพราะ $\nu_t$ คำนวณจาก k และ ε (หรือ ω) ตาม turbulence model: $\nu_t = C_\mu \frac{k^2}{\varepsilon}$
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [04_Mathematical_Formulation.md](04_Mathematical_Formulation.md) — สูตรทางคณิตศาสตร์
- **บทถัดไป:** [06_Advanced_Boundary_Conditions.md](06_Advanced_Boundary_Conditions.md) — BC ขั้นสูง
