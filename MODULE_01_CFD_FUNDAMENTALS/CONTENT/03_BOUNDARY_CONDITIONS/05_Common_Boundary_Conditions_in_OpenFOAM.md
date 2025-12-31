# Common Boundary Conditions in OpenFOAM

รายละเอียดของ BC ที่ใช้บ่อยพร้อม code examples และเหตุผลการใช้งาน

---

## 🎯 Learning Objectives

หลังจากศึกษาบทนี้ คุณจะสามารถ:

1. **เลือก Boundary Condition ที่เหมาะสม** สำหรับ velocity, pressure, temperature และ turbulence ตามประเภทปัญหา
2. **เขียน OpenFOAM BC syntax** ได้อย่างถูกต้องพร้อมค่า parameters ที่เหมาะสม
3. **อธิบายสมมติฐานทางฟิสิกส์** ที่อยู่เบื้องหลังแต่ละ BC type
4. **แก้ไขปัญหา BC** ที่เกิดจากการเลือก BC ผิด หรือตั้งค่าไม่เหมาะสม
5. **คำนวณค่าเริ่มต้น** สำหรับ turbulence quantities (k, ε, ω) จาก flow characteristics
6. **ใช้ BC ขั้นสูง** เช่น inletOutlet, fixedFluxPressure, externalWallHeatFlux ได้อย่างเหมาะสม
7. **ใช้ BC comparison matrix** เพื่อเลือก BC ที่เหมาะสมกับปัญหา
8. **ใช้ decision trees** ในการตัดสินใจเลือก BC
9. **ตรวจสอบความสอดคล้อง** ระหว่าง BCs ของตัวแปรต่าง fields (U, p, T, k, ε, ω)

---

## 3W Framework: What, Why, How

### What: Boundary Conditions คืออะไร?

Boundary Conditions (BCs) คือ **ข้อกำหนดที่ขอบเขตของโดเมนคำนวณ** ที่กำหนดค่าของตัวแปร (U, p, T, k, ε, ω ฯลฯ) หรือ gradient ของมันที่ผิว boundary ใน OpenFOAM BCs ถูกกำหนดในไฟล์ `0/` directory สำหรับแต่ละ field

**ประเภทหลัก:**
- **Dirichlet BC:** กำหนดค่าโดยตรง → `fixedValue`
- **Neumann BC:** กำหนด gradient → `fixedGradient`, `zeroGradient`
- **Robin BC:** ผสมค่าและ gradient → `externalWallHeatFlux`, `inletOutlet`

**โครงสร้างของ BC ใน OpenFOAM:**
```cpp
boundaryName
{
    type            fixedValue;      // BC type
    value           uniform (10 0 0); // Field value(s)
    // Additional parameters depending on BC type
}
```

### Why: ทำไม BC สำคัญ?

> **⚠️ ผลกระทบของ BC ที่ผิด:**
> - Simulation ล้มเหลว (diverge, instability)
> - ผลลัพธ์ผิดทางฟิสิกส์ (non-physical solution)
> - Convergence ช้าลงอย่างมาก
> - Mass/momentum/energy imbalance

BC ที่ถูกต้องรับประกันว่า:
- **Well-posed problem:** มีคำตอบเฉพาะ (unique solution)
- **Physical consistency:** สอดคล้องกับฟิสิกส์จริง
- **Numerical stability:** solver สามารถหาคำตอบได้

**ความสำคัญของ BC consistency:**
- การกำหนด BC สำหรับตัวแปรหนึ่ง (เช่น U) มีผลโดยตรงต่อ BCs ของตัวแปรอื่น (เช่น p)
- การกำหนด BC ที่ขัดแย้งกัน → simulation ไม่ converge หรือให้ผลลัพธ์ผิด

### How: ใช้ BC อย่างไร?

**ขั้นตอนทั่วไป:**
1. **ระบุประเภท boundary:** inlet, outlet, wall, symmetry, cyclic
2. **เลือก BC type:** ตาม physics ของปัญหา (ดู BC comparison matrix และ decision trees)
3. **กำหนดค่า parameters:** เช่น pressure, velocity, heat transfer coefficient
4. **ตรวจสอบ consistency:** ตัวแปรต่างฟิลด์ต้องสอดคล้องกัน (เช่น U กับ p)
5. **ยืนยัน y+ requirements:** สำหรับ turbulence wall functions
6. **ทดสอบและปรับแก้:** ใช้ troubleshooting guide หากเกิดปัญหา

---

## BC Comparison Matrix

### Velocity Boundary Conditions

| BC Type | Dirichlet/Neumann | Use Case | Physics | Key Parameter |
|---------|-------------------|----------|---------|---------------|
| `fixedValue` | Dirichlet | Known velocity profile | U = specified | value |
| `noSlip` | Dirichlet | Viscous wall | U = 0 (no-slip) | - |
| `slip` | Mixed | Inviscid/far-field | uₙ = 0, τ = 0 | - |
| `zeroGradient` | Neumann | Fully developed flow | ∂U/∂n = 0 | - |
| `inletOutlet` | Adaptive | Outlet with possible backflow | Out: ∂U/∂n=0, In: Uₛ | inletValue |
| `pressureInletOutletVelocity` | Adaptive | Outlet with pressure-driven backflow | Out: ∂U/∂n=0, In: U(∇p) | - |
| `pressureInletVelocity` | Calculated | Pressure-driven inlet | U = f(∇p) | value (initial) |
| `freestreamVelocity` | Adaptive | External aero far-field | blends with freestream | freestreamValue |
| `movingWallVelocity` | Dirichlet | Moving wall/belt | U = U_wall | value |

### Pressure Boundary Conditions

| BC Type | Dirichlet/Neumann | Use Case | Physics | Key Parameter |
|---------|-------------------|----------|---------|---------------|
| `fixedValue` | Dirichlet | Pressure reference | p = specified | value |
| `zeroGradient` | Neumann | Inlet/walls (no flux) | ∂p/∂n = 0 | - |
| `totalPressure` | Dirichlet | Stagnation point | p₀ = p + ½ρU² | p0, gamma |
| `freestreamPressure` | Adaptive | External aero | blends with freestream | freestreamValue |
| `fixedFluxPressure` | Neumann | Buoyant flows | ∂p/∂n = ρg·n | value |

### Temperature Boundary Conditions

| BC Type | Dirichlet/Neumann | Use Case | Physics | Key Parameter |
|---------|-------------------|----------|---------|---------------|
| `fixedValue` | Dirichlet | Isothermal wall | T = specified | value |
| `zeroGradient` | Neumann | Adiabatic wall | ∂T/∂n = 0 | - |
| `fixedGradient` | Neumann | Constant heat flux | ∂T/∂n = specified | gradient |
| `externalWallHeatFlux` | Robin | Convection/radiation | q = h(T - T∞) | mode, h/Q/q, Ta |

---

## Decision Trees

### Choosing Velocity BCs

```
Is it a wall?
├─ Yes → Viscous? → Yes → noSlip
│              └─ No → slip
└─ No → Is it inlet?
        ├─ Yes → Know U? → Yes → fixedValue
        │              └─ No → pressureInletVelocity
        └─ No → Is it outlet?
                ├─ Yes → Possible backflow? → Yes → inletOutlet
                │                            └─ No → zeroGradient
                └─ No → Is it far-field?
                        └─ Yes → freestreamVelocity
```

### Choosing Pressure BCs

```
Is it a wall?
├─ Yes → Buoyant? → Yes → fixedFluxPressure
│              └─ No → zeroGradient
└─ No → Is it outlet?
        ├─ Yes → fixedValue (reference pressure!)
        └─ No → Is it inlet with total pressure known?
                └─ Yes → totalPressure
```

### Choosing Temperature BCs

```
Is it a wall?
└─ Yes → Heat transfer known?
        ├─ Yes → Know T? → Yes → fixedValue
        │               └─ No → Know flux? → Yes → fixedGradient
        │                                      └─ No → externalWallHeatFlux
        └─ No → Adiabatic → zeroGradient
```

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

**Physics:**
- Dirichlet BC: U = U_specified ที่ boundary
- เหมาะสำหรับ forced flow ที่รู้ flow rate หรือ velocity

**⚠️ Troubleshooting:**
- **ปัญหา:** Simulation diverge ที่ inlet
- **สาเหตุ:** กำหนด U เท่านั้น แต่ pressure ยังไม่มี reference
- **แก้ไข:** กำหนด `fixedValue` สำหรับ pressure ที่ outlet

- **ปัญหา:** Velocity profile ไม่ realistic หลัง inlet
- **สาเหตุ:** กำหนด uniform value แต่ flow จริงมี profile
- **แก้ไข:** ใช้ `codedFixedValue` หรือ `timeVaryingMappedFixedValue` สำหรับ non-uniform profile

### noSlip

Shorthand สำหรับ fixedValue (0 0 0)

```cpp
wall { type noSlip; }
```

**ทำไมใช้ noSlip?**
- ของไหลจริง "ติด" ผนัง → U = 0 ที่ผิว
- นี่คือ no-slip condition พื้นฐาน
- ใช้สำหรับ viscous flow ทั่วไป

**Physics:**
- No-slip condition: U = 0 ที่ผนังจริง
- Shear stress: τ = μ(∂U/∂y) จะถูกคำนวณอัตโนมัติ

**⚠️ Troubleshooting:**
- **ปัญหา:** y+ สูงเกินไป ทำให้ผิดพลาดใน viscous sublayer
- **สาเหตุ:** ใช้ noSlip กับ mesh หยาบเกินไป
- **แก้ไข:** ใช้ wall functions แทน (ดู turbulence BCs)

- **ปัญหา:** Convergence ช้ามาก
- **สาเหตุ:** Mesh ละเอียดเกินไปใกล้ผนัง → ค่า y+ ต่ำเกินไป
- **แก้ไข:** ใช้ wall functions หรือใช้ low-Re turbulence models

### slip

ไม่มี shear stress, ความเร็ว normal = 0

```cpp
symmetryWall { type slip; }
```

**ใช้เมื่อ:**
- Inviscid simulation (ไม่สนใจ viscosity)
- Far-field boundary ที่ไม่ต้องการ friction
- Symmetry plane (เทียบเท่ากับ `symmetry` BC)

**Physics:** $u_n = 0$, $\tau = 0$

- Flow ผ่านผนังโดยไม่มี friction
- เหมาะสำหรับ inviscid flow (Euler equations)

**⚠️ Troubleshooting:**
- **ปัญหา:** Shear layer ไม่ถูกต้อง
- **สาเหตุ:** ใช้ slip กับ viscous flow
- **แก้ไข:** เปลี่ยนเป็น noSlip สำหรับผนังจริง

- **ปัญหา:** Mass loss ที่ slip boundary
- **สาเหตุ:** ใช้ slip แต่ mesh ไม่ aligned กับ flow direction
- **แก้ไข:** ตรวจสอบว่า boundary normal ตั้งฉากกับ flow direction

### zeroGradient

Extrapolate จาก internal field

```cpp
outlet { type zeroGradient; }
```

**ทำไมใช้ที่ outlet?**
- สมมติ flow พัฒนาเต็มที่ (fully developed)
- Profile ไม่เปลี่ยนแปลง → $\partial U/\partial n = 0$

**Physics:**
- Neumann BC: ∂U/∂n = 0
- Flow ที่ outlet มี profile เหมือนกับตัวก่อนหน้า

**⚠️ Troubleshooting:**
- **ปัญหา:** Backflow เกิดขึ้น และ simulation ล้มเหลว
- **สาเหตุ:** zeroGradient ไม่รู้จักการไหลกลับเข้า
- **แก้ไข:** ใช้ `inletOutlet` แทน

- **ปัญหา:** Velocity ที่ outlet ไม่ realistic
- **สาเหตุ:** Outlet ใกล้กับ region ที่สนใจมากเกินไป
- **แก้ไข:** ขยายโดเมน ให้ outlet ห่างจาก region ที่สนใจ

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

**Physics:**
- Flow ออก: ∂U/∂n = 0
- Flow เข้า: U = inletValue

**⚠️ Troubleshooting:**
- **ปัญหา:** Backflow มี direction ผิด
- **สาเหตุ:** `inletValue` ไม่สอดคล้องกับ pressure field
- **แก้ไข:** ใช้ `pressureInletOutletVelocity` แทน (คำนวณ U จาก ∇p)

- **ปัญหา:** Backflow มีมากเกินไป
- **สาเหตุ:** Outlet ใกล้กับ region ที่มี recirculation มากเกินไป
- **แก้ไข:** ขยายโดเมน หรือใช้ `pressureInletOutletVelocity`

### pressureInletOutletVelocity

เป็นตัวแปรที่จัดการ backflow อัตโนมัติเช่นกัน แต่จะคำนวณความเร็วจากความดัน

```cpp
outlet
{
    type    pressureInletOutletVelocity;
    value   uniform (0 0 0);
}
```

**ใช้เมื่อ:**
- มี backflow ที่ outlet และต้องการให้ velocity สอดคล้องกับ pressure field
- ใช้ร่วมกับ `fixedFluxPressure` หรือ `zeroGradient` สำหรับ pressure

**Physics:**
- Flow ออก: ∂U/∂n = 0
- Flow เข้า: U = -∇p/(μ|U|) คำนวณจาก pressure gradient

**⚠️ Troubleshooting:**
- **ปัญหา:** Convergence ไม่ดี
- **สาเหตุ:** ใช้ `pressureInletOutletVelocity` แต่ pressure BC ไม่เหมาะสม
- **แก้ไข:** ใช้ร่วมกับ `fixedFluxPressure` สำหรับ pressure

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

**Physics:**
- U คำนวณจาก pressure gradient: U = -K∇p
- เหมาะสำหรับ natural convection หรือ pressure-driven flow

**⚠️ Troubleshooting:**
- **ปัญหา:** Velocity inlet ไม่สมดุล mass
- **สาเหตุ:** กำหนด pressure ไว้ไม่ดี หรือไม่มี pressure outlet
- **แก้ไข:** ตรวจสอบว่ามี pressure reference point เช่น `fixedValue` ที่ outlet

- **ปัญหา:** Mass flow rate ไม่คงที่
- **สาเหตุ:** ไม่ได้กำหนด pressure reference ที่ชัดเจน
- **แก้ไข:** กำหนด `fixedValue` สำหรับ pressure ที่ outlet

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

**Physics:**
- ใช้ร่วมกับ `freestreamPressure`
- Blend ระหว่าง freestream value กับ computed value ตาม distance

**⚠️ Troubleshooting:**
- **ปัญหา:** Freestream BCs สร้าง reflection
- **สาเหตุ:** ขอบเขตใกล้กับ body มากเกินไป
- **แก้ไข:** ขยายโดเมน หรือใช้ far-field ที่เหมาะสมกว่า

- **ปัญหา:** Non-physical waves ที่ freestream boundary
- **สาเหตุ:** ไม่ได้ใช้ `freestreamPressure` ร่วมกับ `freestreamVelocity`
- **แก้ไข:** ใช้ทั้งคู่ร่วมกัน

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

**Physics:**
- U_wall = U_specified
- ของไหลที่ผนังมีความเร็วเท่ากับผนัง

**⚠️ Troubleshooting:**
- **ปัญหา:** Mesh distortion หรือ negative volumes
- **สาเหตุ:** ใช้ `movingWallVelocity` กับ moving mesh ผิดวิธี
- **แก้ไข:** ตรวจสอบว่า mesh คงที่ (stationary mesh) หรือใช้ dynamic mesh solvers

- **ปัญหา:** Shear stress ไม่ถูกต้อง
- **สาเหตุ:** ไม่ได้กำหนดความเร็วอย่างถูกต้อง
- **แก้ไข:** ตรวจสอบว่า velocity magnitude และ direction ถูกต้อง

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

**Physics:**
- กำหนด p = p_ref ที่ boundary
- สำคัญมากสำหรับ incompressible flow (pressure จะ drift ถ้าไม่มี reference)

**⚠️ Troubleshooting:**
- **ปัญหา:** Pressure drift หรือไม่ converge
- **สาเหตุ:** กำหนด `fixedValue` มากเกินไป (over-constrained)
- **แก้ไข:** กำหนด fixedValue เพียงจุดเดียว ให้ BCs อื่นเป็น zeroGradient

- **ปัญหา:** Pressure field ไม่สมดุล
- **สาเหตุ:** กำหนด `fixedValue` สำหรับ pressure ที่ inlet และ outlet
- **แก้ไข:** กำหนด `fixedValue` จุดเดียว (มักเป็น outlet) ให้อีกจุดเป็น `zeroGradient`

### zeroGradient

ปล่อยให้ p ปรับตัวตามธรรมชาติ

```cpp
inlet { type zeroGradient; }
wall  { type zeroGradient; }
```

**ใช้เมื่อ:**
- Inlet ที่กำหนด U แล้ว (ปล่อยให้ p คำนวณมา)
- Wall ทั่วไป (ไม่มี pressure flux ผ่านผนัง)

**Physics:**
- ∂p/∂n = 0 → ไม่มี pressure gradient ผ่าน boundary
- Pressure คำนวณจาก continuity equation

**⚠️ Troubleshooting:**
- **ปัญหา:** Pressure field ไม่สเถียร
- **สาเหตุ:** กำหนด zeroGradient ทุก boundary ไม่มี reference
- **แก้ไข:** ต้องมีอย่างน้อยหนึ่งจุดที่เป็น `fixedValue`

- **ปัญหา:** Pressure oscillation
- **สาเหตุ:** ใช้ `zeroGradient` สำหรับ pressure ที่ inlet ที่มี velocity fluctuation
- **แก้ไข:** ใช้ `totalPressure` แทน

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

- Total pressure = static pressure + dynamic pressure
- ใช้สำหรับ compressible flow หรือ high-Mach flow

**⚠️ Troubleshooting:**
- **ปัญหา:** Mass flow rate ไม่ถูกต้อง
- **สาเหตุ:** กำหนด total pressure แต่ไม่ได้กำหนด velocity BCs ที่สอดคล้องกัน
- **แก้ไข:** ใช้ `totalPressure` ร่วมกับ `pressureInletVelocity` ที่ inlet เดียวกัน

- **ปัญหา:** Pressure ไม่ converge
- **สาเหตุ:** กำหนด `totalPressure` ที่ inlet และ outlet
- **แก้ไข:** กำหนด `totalPressure` จุดเดียว ให้อีกจุดเป็น `fixedValue`

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

**Physics:**
- Blend ระหว่าง freestream value กับ computed value
- ใช้สำหรับ external aerodynamics

**⚠️ Troubleshooting:**
- **ปัญหา:** Non-physical pressure waves
- **สาเหตุ:** Freestream boundary ใกล้ object มากเกินไป
- **แก้ไข:** ขยายโดเมน ให้ farfield ห่างจาก body อย่างน้อย 5-10 characteristic lengths

- **ปัญหา:** Pressure ไม่ realistic
- **สาเหตุ:** ไม่ได้ใช้ `freestreamVelocity` ร่วมกับ `freestreamPressure`
- **แก้ไข:** ใช้ทั้งคู่ร่วมกัน

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

**Physics:**
- ∂p/∂n = ρg·n → pressure gradient เพื่อรักษา mass flux
- สำคัญสำหรับ buoyant flow ที่มี gravity

**⚠️ Troubleshooting:**
- **ปัญหา:** Vertical velocity artifacts ใน buoyant flow
- **สาเหตุ:** ใช้ `zeroGradient` แทน `fixedFluxPressure` ที่ผนัง
- **แก้ไข:** เปลี่ยนเป็น `fixedFluxPressure` สำหรับผนังทั้งหมดใน buoyant cases

- **ปัญหา:** Pressure ไม่ converge
- **สาเหตุ:** ไม่ได้กำหนด pressure reference
- **แก้ไข:** กำหนด `fixedValue` สำหรับ pressure ที่ outlet

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

**Physics:**
- Dirichlet BC: T = T_specified
- ใช้สำหรับผนังที่มีการควบคุมอุณหภูมิ

**⚠️ Troubleshooting:**
- **ปัญหา:** อุณหภูมิผนังไม่สมดุลกับ heat flux
- **สาเหตุ:** กำหนด T คงที่ แต่ heat source/sink ไม่สมดุล
- **แก้ไข:** ใช้ `externalWallHeatFlux` แทน เพื่อให้สมดุล energy

- **ปัญหา:** Temperature gradient สูงผิดปกติ
- **สาเหตุ:** Mesh หยาบเกินไปใกล้ผนัง
- **แก้ไข:** ยุบ mesh ใกล้ผนัง หรือใช้ wall functions

### zeroGradient

ผนัง adiabatic (ไม่มี heat transfer)

```cpp
insulated { type zeroGradient; }
```

**Physics:** $\partial T/\partial n = 0$ → $q = 0$

- ไม่มี heat flux ผ่านผนัง
- ใช้สำหรับ insulated wall

**⚠️ Troubleshooting:**
- **ปัญหา:** อุณหภูมิในโดเมนสูงขึ้นเรื่อยๆ ไม่ stabilise
- **สาเหตุ:** ไม่มี heat sink (ทุกผนังเป็น adiabatic)
- **แก้ไข:** เพิ่มผนังที่มี heat flux ออก (fixedValue หรือ externalWallHeatFlux)

- **ปัญหา:** Temperature ไม่สมดุล
- **สาเหตุ:** Heat source ในโดเมน แต่ไม่มี heat sink
- **แก้ไข:** เพิ่มผนังที่มี heat flux ออก

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

**⚠️ Troubleshooting:**
- **ปัญหา:** Heat flux ผิดค่า
- **สาเหตุ:** ใส่ค่า heat flux โดยตรง แต่ BC ต้องการ temperature gradient
- **แก้ไข:** แปลง heat flux → temperature gradient: ∇T = -q''/k
  - เช่น: ต้องการ q'' = 5000 W/m², k = 50 W/(m·K)
  - ∇T = -5000/50 = -100 K/m
  - ใส่ `gradient uniform -100;`

- **ปัญหา:** Temperature ไม่ converge
- **สาเหตุ:** กำหนด gradient สูงเกินไป → heat flux สูงเกินไป
- **แก้ไข:** ลดค่า gradient หรือเพิ่ม under-relaxation สำหรับ energy equation

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
- คำนวณ temperature gradient อัตโนมัติ

**⚠️ Troubleshooting:**
- **ปัญหา:** อุณหภูมิผนังไม่ converge
- **สาเหตุ:** Heat transfer coefficient h สูงเกินไป → stiff system
- **แก้ไข:** ลดค่า h หรือเพิ่ม under-relaxation สำหรับ energy equation

- **ปัญหา:** Heat balance ไม่สมดุล
- **สาเหตุ:** ไม่ได้กำหนด heat sink ที่ชัดเจน
- **แก้ไข:** ตรวจสอบว่า heat in = heat out

- **ปัญหา:** Temperature ไม่ realistic
- **สาเหตุ:** กำหนด h ผิด หรือ T_ambient ผิด
- **แก้ไข:** ตรวจสอบค่า h และ T_ambient ให้ถูกต้อง

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

**⚠️ Troubleshooting:**
- **ปัญหา:** Turbulence viscosity สูงผิดปกติ (nut → ∞)
- **สาเหตุ:** k สูง แต่ ε ต่ำเกินไป
- **แก้ไข:** ตรวจสอบสูตรคำนวณ ε และ ω (ดูด้านล่าง) ให้สัดส่วนถูกต้อง

- **ปัญหา:** Turbulence quantities ไม่ realistic
- **สาเหตุ:** กำหนดค่า k, ε, ω ไม่ถูกต้อง
- **แก้ไข:** ใช้สูตรคำนวณ (ดูด้านล่าง) หรือใช้ turbulence generator

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

**⚠️ Troubleshooting:**
- **ปัญหา:** Skin friction ผิด หรือ convergence ไม่ดี
- **สาเหตุ:** y+ อยู่นอกช่วง 30-300
  - y+ < 30: อยู่ใน viscous sublayer → wall functions ผิด
  - y+ > 300: อยู่ไกลเกินไป → resolution ไม่พอ
- **แก้ไข:**
  - ถ้า y+ ต่ำเกิน: ขยาย mesh ใกล้ผนัง (first cell ห่างออก)
  - ถ้า y+ สูงเกิน: ยุบ mesh ใกล้ผนัง (first cell ใกล้ขึ้น)
  - หรือใช้ low-Re models ที่ resolve viscous sublayer

- **ปัญหา:** Wall functions ไม่ทำงาน
- **สาเหตุ:** ไม่ได้กำหนด wall function types สำหรับทุก turbulence fields
- **แก้ไข:** ตรวจสอบว่า k, ε/ω, nut ใช้ wall functions ครบ

### At Outlet

```cpp
// ทุก turbulence field
outlet { type zeroGradient; }
```

**ทำไม?** ปล่อยให้ turbulent quantities ไหลออกอิสระ

**⚠️ Troubleshooting:**
- **ปัญหา:** Turbulence quantities ไม่ realistic ที่ outlet
- **สาเหตุ:** Outlet ใกล้กับ region ที่น่าสนใจเกินไป
- **แก้ไข:** ขยายโดเมน ให้ outlet ห่างจาก region ที่สนใจอย่างน้อย 10 characteristic lengths

- **ปัญหา:** Turbulence backflow
- **สาเหตุ:** ไม่ได้จัดการ backflow สำหรับ turbulence
- **แก้ไข:** ใช้ `inletOutlet` สำหรับ k, ε, ω

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

**ใช้เมื่อ:**
- Flow มี symmetry จริงๆ
- ต้องการลดขนาดโดเมน

**⚠️ Troubleshooting:**
- **ปัญหา:** Mass imbalance หรือ non-physical asymmetry
- **สาเหตุ:** ใช้ symmetry กับ flow ที่ไม่สมมาตรจริง
- **แก้ไข:** ตรวจสอบว่า flow จริงๆ มี symmetry หรือไม่ ถ้าไม่แน่ใจใช้ full domain

- **ปัญหา:** Solver error "symmetry plane not aligned"
- **สาเหตุ:** Symmetry plane ไม่ aligned กับ coordinate axes
- **แก้ไข:** ตรวจสอบว่า symmetry plane ตั้งฉากกับ coordinate axes

### cyclic

Periodic boundary (ต้องกำหนดใน polyMesh/boundary ด้วย)

```cpp
left  { type cyclic; }
right { type cyclic; }
```

**ใช้เมื่อ:** Flow เป็น pattern ซ้ำๆ (pipe, heat exchanger)

**Physics:**
- ค่าที่ boundary หนึ่ง = ค่าที่ boundary อีกข้าง
- Mass/momentum/energy ผ่าน cyclic boundary ได้

**⚠️ Troubleshooting:**
- **ปัญหา:** Simulation ไม่ converge
- **สาเหตุ:** Face meshes ที่ cyclic boundaries ไม่ตรงกัน
- **แก้ไข:** ใช้ `createPatch` หรือแก้ไข `polyMesh/boundary` ให้ matching

- **ปัญหา:** "Cyclic patches not matching" error
- **สาเหตุ:** Cyclic patches ไม่มีจำนวน faces เท่ากัน
- **แก้ไข:** ใช้ `createNonConformalCyclicPairs` หรือสร้าง mesh ใหม่

### empty

2D simulation (ไม่มี flux ในทิศทางนั้น)

```cpp
frontAndBack { type empty; }
```

**ใช้เมื่อ:** Mesh มี 1 cell ในทิศทาง z (pseudo-2D)

**Physics:**
- ไม่มี flux ในทิศทางที่เป็น empty
- ใช้สำหรับ 2D simulation

**⚠️ Troubleshooting:**
- **ปัญหา:** "empty boundary in 3D case" error
- **สาเหตุ:** ใช้ `empty` กับ mesh 3D จริง
- **แก้ไข:** ตรวจสอบว่า mesh มี 1 cell เท่านั้น ในทิศทางที่เป็น empty

- **ปัญหา:** Solver ไม่รับรู้จัก empty boundary
- **สาเหตุ:** ใช้ `empty` กับ solver ที่ไม่รองรับ 2D
- **แก้ไข:** ใช้ solver ที่รองรับ 2D หรือเปลี่ยนเป็น `symmetry`

### wedge

Axisymmetric simulation

```cpp
wedgeFront { type wedge; }
wedgeBack  { type wedge; }
```

**ใช้เมื่อ:** ปัญหา axisymmetric (pipe, nozzle, jet)

**Physics:**
- ใช้สำหรับ axisymmetric flow
- ลดขนาดโดเมนเหลือเพียง 1 wedge

**⚠️ Troubleshooting:**
- **ปัญหา:** "wedge patch angles do not match" error
- **สาเหตุ:** มุม wedge ไม่เป็นคู่ หรือไม่อยู่ในตำแหน่งที่ถูกต้อง
- **แก้ไข:** ตรวจสอบว่า wedge front และ back สร้างมุมเดียวกัน (< 5° แนะนำ)

- **ปัญหา:** "wedge patches not aligned" error
- **สาเหตุ:** Wedge patches ไม่ aligned กับ axis of symmetry
- **แก้ไข:** ตรวจสอบว่า wedge patches อยู่บน axis of symmetry

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

<details>
<summary><b>5. ต้องตรวจสอบอะไรบ้างเมื่อเลือก BC?</b></summary>

**Checklist:**
1. ✅ มี pressure reference point (`fixedValue` สำหรับ p)
2. ✅ U และ p BCs สอดคล้องกัน
3. ✅ y+ อยู่ในช่วงที่เหมาะสมสำหรับ wall functions
4. ✅ Backflow ได้รับการจัดการ (ใช้ inletOutlet/pressureInletOutletVelocity)
5. ✅ Heat balance สมดุล (heat in = heat out)
6. ✅ Turbulence quantities มีสัดส่วนถูกต้อง
</details>

---

## 📋 Key Takeaways

### Boundary Condition Selection

1. **Inlet:**
   - Velocity-known → `fixedValue` for U
   - Pressure-driven → `pressureInletVelocity` for U + `totalPressure` for p
   - External aero → `freestreamVelocity`

2. **Outlet:**
   - Standard → `inletOutlet` for U (handles backflow)
   - Pressure reference → `fixedValue` for p (usually 0 gauge)
   - Backflow concern → `pressureInletOutletVelocity`

3. **Wall:**
   - Viscous → `noSlip` for U
   - Inviscid → `slip` for U
   - Adiabatic → `zeroGradient` for T
   - Isothermal → `fixedValue` for T
   - Convection → `externalWallHeatFlux` for T
   - Buoyant → `fixedFluxPressure` for p

4. **Turbulence:**
   - Inlet → `fixedValue` for k, ε, ω + `calculated` for nut
   - Wall → Wall functions (check y+ 30-300!)
   - Outlet → `zeroGradient`

### Common Pitfalls

- ❌ กำหนด `fixedValue` สำหรับ pressure ที่ทุก boundary → **pressure drift**
- ✅ กำหนด `fixedValue` จุดเดียว ให้ศักย์อื่นเป็น `zeroGradient`

- ❌ ใช้ `zeroGradient` สำหรับ U ที่ outlet → **backflow instability**
- ✅ ใช้ `inletOutlet` หรือ `pressureInletOutletVelocity`

- ❌ ใช้ `zeroGradient` สำหรับ p ที่ผนังใน buoyant flow → **artifacts**
- ✅ ใช้ `fixedFluxPressure` สำหรับ buoyant flows

- ❌ ใช้ wall functions กับ y+ < 5 → **incorrect skin friction**
- ✅ ตรวจสอบ y+ อยู่ในช่วง 30-300

- ❌ ใส่ heat flux โดยตรงใน `fixedGradient` → **wrong flux**
- ✅ แปลง: ∇T = -q''/k

### Troubleshooting Workflow

1. **Simulation diverges?**
   - ตรวจสอบ BCs ที่ inlet/outlet มี pressure reference หรือยัง
   - ตรวจสอสอดคล้องระหว่าง U และ p BCs

2. **Backflow problems?**
   - เปลี่ยน `zeroGradient` → `inletOutlet` หรือ `pressureInletOutletVelocity`
   - ขยาย outlet ให้ไกลจาก region ที่สนใจ

3. **y+ out of range?**
   - y+ < 30: ขยาย first cell หรือใช้ low-Re model
   - y+ > 300: ยุบ mesh ใกล้ผนัง

4. **Temperature not converging?**
   - ลด h ใน `externalWallHeatFlux`
   - ตรวจสอบ energy balance (heat in = heat out)

5. **Turbulence quantities unrealistic?**
   - ตรวจสอบสูตรคำนวณ k, ε, ω
   - ตรวจสอบว่า nut ใช้ `calculated`

### Quick Reference

| Scenario | U BC | p BC | T BC |
|----------|------|------|------|
| Pipe flow (inlet U) | fixedValue | zeroGradient | - |
| Pipe flow (outlet p) | inletOutlet | fixedValue | - |
| Natural convection | zeroGradient | fixedFluxPressure | fixedValue / externalWallHeatFlux |
| External aerodynamics | freestreamVelocity | freestreamPressure | - |
| Fan (inlet p₀) | pressureInletVelocity | totalPressure | - |
| Heat exchanger | fixedValue / cyclic | zeroGradient | fixedValue / externalWallHeatFlux |

---

## Navigation

**📑 ในบทนี้:**
- [03_Selection_Guide_Which_BC_to_Use.md](03_Selection_Guide_Which_BC_to_Use.md) — ตัวช่วยเลือก BC อย่างไร (ตัวช่วย decision trees)
- [04_Mathematical_Formulation.md](04_Mathematical_Formulation.md) — สูตรทางคณิตศาสตาร์

**บทที่เกี่ยวข้อง:**
- **บทก่อนหน้า:** [02_Fundamental_Classification.md](02_Fundamental_Classification.md) — ประเภท BC พื้นฐาน (Dirichlet, Neumann, Robin)
- **บทถัดไป:** [06_Advanced_Boundary_Conditions.md](06_Advanced_Boundary_Conditions.md) — BC ขั้นสูง (time-dependent, coupled, etc.)