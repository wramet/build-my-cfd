# Common Boundary Conditions in OpenFOAM

รายละเอียดของ BC ที่ใช้บ่อยพร้อม code examples และเหตุผลการใช้งาน

> **ทำไมต้องเข้าใจ BC แต่ละตัว?**
> - BC ที่เลือกผิดอาจทำให้ simulation ล้มเหลวหรือให้ผลผิด
> - แต่ละ BC มี **สมมติฐานทางกายภาพ** ที่ต้องเข้าใจ
> - การรู้ options ทำให้เลือกได้เหมาะสมกับปัญหา

---

## Velocity BCs

### fixedValue

กำหนดค่าความเร็วโดยตรง

```cpp
inlet
{
    type    fixedValue;
    value   uniform (10 0 0);   // 10 m/s ในทิศ x
}
```

**ใช้เมื่อ:** รู้ velocity profile ที่ inlet

### noSlip

Shorthand สำหรับ fixedValue (0 0 0)

```cpp
wall { type noSlip; }
```

**ทำไมใช้ noSlip?**
- ของไหลจริง "ติด" ผนัง → U = 0 ที่ผิว
- นี่คือ no-slip condition พื้นฐาน

### slip

ไม่มี shear stress, ความเร็ว normal = 0

```cpp
symmetryWall { type slip; }
```

**ใช้เมื่อ:**
- Inviscid simulation (ไม่สนใจ viscosity)
- Far-field boundary ที่ไม่ต้องการ friction

**Physics:** $u_n = 0$, $\tau = 0$

### zeroGradient

Extrapolate จาก internal field

```cpp
outlet { type zeroGradient; }
```

**ทำไมใช้ที่ outlet?**
- สมมติ flow พัฒนาเต็มที่ (fully developed)
- Profile ไม่เปลี่ยนแปลง → $\partial U/\partial n = 0$

### inletOutlet

จัดการ backflow อัตโนมัติ — **แนะนำสำหรับ outlet!**

```cpp
outlet
{
    type        inletOutlet;
    inletValue  uniform (0 0 0);    // ใช้ถ้า flow กลับเข้า
    value       uniform (10 0 0);   // initial guess
}
```

**ทำไมดีกว่า zeroGradient?**
- zeroGradient ไม่จัดการ backflow → อาจ diverge
- inletOutlet: ไหลออก = zeroGradient, ไหลเข้า = inletValue

### pressureInletVelocity

คำนวณ U จาก pressure gradient

```cpp
inlet
{
    type    pressureInletVelocity;
    value   uniform (0 0 0);    // initial guess
}
```

**ใช้เมื่อ:** รู้ pressure ไม่รู้ velocity (pressure-driven flow)

### freestreamVelocity

Far-field สำหรับ external flow

```cpp
farField
{
    type            freestreamVelocity;
    freestreamValue uniform (50 0 0);
}
```

**ทำไมใช้สำหรับ external aero?**
- Freestream = ห่างจาก body พอ → flow ไม่ถูกรบกวน
- ปรับตัวตาม local flow direction

### movingWallVelocity

ผนังเคลื่อนที่

```cpp
belt
{
    type    movingWallVelocity;
    value   uniform (1 0 0);
}
```

**ใช้เมื่อ:** Conveyor belt, rotating disk, car wheel on ground

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

**ทำไมใช้ที่ outlet?**
- เป็น **reference point** สำหรับ pressure
- ถ้าไม่มี reference → p สามารถ drift ได้ (Poisson equation)

### zeroGradient

ปล่อยให้ p ปรับตัวตามธรรมชาติ

```cpp
inlet { type zeroGradient; }
wall  { type zeroGradient; }
```

**ใช้เมื่อ:**
- Inlet ที่กำหนด U แล้ว (ปล่อยให้ p คำนวณมา)
- Wall ทั่วไป (ไม่มี pressure flux ผ่านผนัง)

### totalPressure

กำหนด total pressure (รวม dynamic head)

```cpp
inlet
{
    type    totalPressure;
    p0      uniform 10000;  // Pa (total)
    gamma   1.4;            // สำหรับ compressible
}
```

**ใช้เมื่อ:** รู้ stagnation pressure

**Physics:** $p_0 = p + \frac{1}{2}\rho|U|^2$

### freestreamPressure

Far-field pressure

```cpp
farField
{
    type            freestreamPressure;
    freestreamValue uniform 0;
}
```

**ใช้คู่กับ:** `freestreamVelocity` สำหรับ external aero

### fixedFluxPressure

รักษา mass flux ที่กำหนด — **สำหรับ buoyant flows**

```cpp
wall
{
    type    fixedFluxPressure;
    value   uniform 0;
}
```

**ทำไมใช้แทน zeroGradient?**
- ถ้ามี body force (gravity): $\partial p/\partial n \neq 0$
- `fixedFluxPressure` จัดการอัตโนมัติ

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

**ใช้เมื่อ:** ผนังรักษาอุณหภูมิคงที่ (isothermal wall)

### zeroGradient

ผนัง adiabatic (ไม่มี heat transfer)

```cpp
insulated { type zeroGradient; }
```

**Physics:** $\partial T/\partial n = 0$ → $q = 0$

### fixedGradient

Heat flux คงที่

```cpp
heatedWall
{
    type        fixedGradient;
    gradient    uniform 1000;   // K/m
}
```

**Physics:**
$$\frac{\partial T}{\partial n} = 1000 \text{ K/m}$$

**Heat flux ที่เกิดขึ้น:**
$$q'' = -k \frac{\partial T}{\partial n}$$

ถ้า $k = 50$ W/(m·K) (เหล็ก):
$$q'' = -50 \times 1000 = -50,000 \text{ W/m}^2$$

> **⚠️ สำคัญ:** `gradient` field คือ **temperature gradient** ไม่ใช่ heat flux
> - Input: $\partial T/\partial n$ [K/m]
> - Actual flux: $q'' = -k \cdot \nabla T$ [W/m²]
> - Gradient เป็นบวก → heat flows OUT (cooling)
> - Gradient เป็นลบ → heat flows IN (heating) ในระบบ coordinate ที่ถูกต้อง

### externalWallHeatFlux

Convective/radiative heat transfer — **ยืดหยุ่นที่สุด!**

```cpp
// Coefficient mode (Newton's cooling: q = h(T_wall - T_ambient))
convWall
{
    type    externalWallHeatFlux;
    mode    coefficient;
    h       uniform 10;     // W/(m²·K) - heat transfer coefficient
    Ta      uniform 300;    // K - ambient temperature
}

// Power mode (กำหนด total heat)
heater
{
    type    externalWallHeatFlux;
    mode    power;
    Q       100;            // W [total heat] = 100 Joules/sec
}

// Flux mode (กำหนด heat flux)
fluxWall
{
    type    externalWallHeatFlux;
    mode    flux;
    q       uniform 5000;   // W/m² [heat flux per unit area]
}
```

**คำอธิบาย:**
- **Coefficient mode:** $q = h(T_{wall} - T_{ambient})$ — ใช้ convection coefficient
- **Power mode:** ใส่ค่า **Total power** [W] ไม่ใช่ flux (จะถูกกระจายออกทั้งผิว)
- **Flux mode:** ใส่ค่า **Heat flux** [W/m²] ต่อหน่วยพื้นที่

**ทำไมดีกว่า fixedGradient?**
- ใช้ h และ T_ambient โดยตรง (intuitive)
- รองรับหลาย modes

---

## Turbulence BCs

### At Inlet

```cpp
// k (turbulent kinetic energy)
inlet
{
    type    fixedValue;
    value   uniform 0.1;    // m²/s² (ดูสูตรคำนวณด้านล่าง)
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
    type    calculated;     // คำนวณจาก k และ ε/ω
    value   uniform 0;
}
```

**ทำไม nut ใช้ calculated?**
- $\nu_t = C_\mu \frac{k^2}{\varepsilon}$ หรือ $\nu_t = \frac{k}{\omega}$
- คำนวณจาก k และ ε/ω อัตโนมัติ

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
    Cmu     0.09;     // Model constant
    kappa   0.41;     // von Karman constant
    E       9.8;      // Log-law constant
}
```

**ทำไมใช้ Wall Functions?**
- ไม่ต้อง resolve viscous sublayer (y+ < 5)
- ประหยัด cells ใกล้ผนังมหาศาล

**ต้องมี y+ ในช่วง 30-300!**

### At Outlet

```cpp
// ทุก turbulence field
outlet { type zeroGradient; }
```

**ทำไม?** ปล่อยให้ turbulent quantities ไหลออกอิสระ

---

## Special BCs

### symmetry

สมมาตร — ลดขนาดโดเมนครึ่งหนึ่ง

```cpp
symmetryPlane { type symmetry; }
```

**Physics:**
- $u_n = 0$ (no flow across symmetry)
- $\partial \phi / \partial n = 0$ for scalars

### cyclic

Periodic boundary (ต้องกำหนดใน polyMesh/boundary ด้วย)

```cpp
left  { type cyclic; }
right { type cyclic; }
```

**ใช้เมื่อ:** Flow เป็น pattern ซ้ำๆ (pipe, heat exchanger)

### empty

2D simulation (ไม่มี flux ในทิศทางนั้น)

```cpp
frontAndBack { type empty; }
```

**ใช้เมื่อ:** Mesh มี 1 cell ในทิศทาง z (pseudo-2D)

### wedge

Axisymmetric simulation

```cpp
wedgeFront { type wedge; }
wedgeBack  { type wedge; }
```

**ใช้เมื่อ:** ปัญหา axisymmetric (pipe, nozzle, jet)

---

## BC Estimation Formulas

### Turbulent Intensity

$$I = \frac{u'}{U} \approx 0.01 - 0.10$$

- **1-5%:** Low turbulence (clean wind tunnel)
- **5-10%:** Moderate turbulence (internal flows)

### Turbulent Kinetic Energy

$$k = \frac{3}{2}(U \cdot I)^2$$

**ตัวอย่าง:** U = 10 m/s, I = 5% → k = 1.5 × (10 × 0.05)² = 0.375 m²/s²

### Dissipation Rate (epsilon)

$$\varepsilon = C_\mu^{3/4} \frac{k^{3/2}}{l}$$

โดย $l \approx 0.07 D$ (hydraulic diameter), $C_\mu = 0.09$

### Specific Dissipation (omega)

$$\omega = \frac{\varepsilon}{C_\mu k} = \frac{k^{1/2}}{C_\mu^{1/4} l}$$

---

## Concept Check

<details>
<summary><b>1. inletOutlet กับ pressureInletOutletVelocity ต่างกันอย่างไร?</b></summary>

| | inletOutlet | pressureInletOutletVelocity |
|-|-------------|----------------------------|
| Flow ออก | zeroGradient | zeroGradient |
| Flow กลับ | ใช้ `inletValue` ที่กำหนด | **คำนวณ U จาก pressure** |

**ใช้ pressureInletOutletVelocity เมื่อ:** ต้องการให้ backflow มี direction ถูกต้องตาม pressure
</details>

<details>
<summary><b>2. totalPressure ใช้เมื่อไหร่?</b></summary>

**ใช้เมื่อ:** ต้องการรักษา stagnation pressure คงที่ ที่ inlet

**Physics:** $p_0 = p + \frac{1}{2}\rho|U|^2$

**ตัวอย่าง:** Fan inlet, compressor inlet ที่รู้ total pressure แต่ไม่รู้ velocity
</details>

<details>
<summary><b>3. ทำไม nut ใช้ calculated ที่ inlet?</b></summary>

**เหตุผล:** $\nu_t$ ไม่ใช่ตัวแปรอิสระ — มันคำนวณจาก k และ ε/ω

**สูตร:**
- k-ε: $\nu_t = C_\mu \frac{k^2}{\varepsilon}$
- k-ω: $\nu_t = \frac{k}{\omega}$

ถ้ากำหนด k และ ε/ω แล้ว → nut คำนวณอัตโนมัติ
</details>

<details>
<summary><b>4. fixedFluxPressure กับ zeroGradient ต่างกันอย่างไร?</b></summary>

| | zeroGradient | fixedFluxPressure |
|-|--------------|-------------------|
| Physics | $\partial p/\partial n = 0$ | $\partial p/\partial n = \rho \mathbf{g} \cdot \mathbf{n}$ |
| ใช้เมื่อ | ไม่มี body force | มี gravity หรือ buoyancy |

**ถ้าใช้ผิด:** Buoyant flow จะมี artifacts ที่ผนัง
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [04_Mathematical_Formulation.md](04_Mathematical_Formulation.md) — สูตรทางคณิตศาสตร์
- **บทถัดไป:** [06_Advanced_Boundary_Conditions.md](06_Advanced_Boundary_Conditions.md) — BC ขั้นสูง
- **คู่มือเลือก BC:** [03_Selection_Guide_Which_BC_to_Use.md](03_Selection_Guide_Which_BC_to_Use.md)
