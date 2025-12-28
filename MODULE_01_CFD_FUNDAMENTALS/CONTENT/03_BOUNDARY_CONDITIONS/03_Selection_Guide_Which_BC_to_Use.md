# คู่มือการเลือก Boundary Condition

Decision guide สำหรับเลือก BC ที่เหมาะสมกับแต่ละสถานการณ์

> **ทำไม BC สำคัญมาก?**
> - BC ผิด = คำตอบผิด (แม้ mesh ดีและ settings ถูกต้อง)
> - หลายครั้ง simulation diverge เพราะ BC ไม่เหมาะสม
> - BC ที่ถูกต้องต้องสะท้อน **physics จริง** ของปัญหา

---

## Quick Reference Table

| สถานการณ์ | Velocity (U) | Pressure (p) | ทำไม |
|-----------|-------------|--------------|------|
| **Velocity inlet** | `fixedValue` | `zeroGradient` | กำหนด U → ปล่อย p ปรับตัว |
| **Pressure inlet** | `pressureInletVelocity` | `fixedValue` | กำหนด p → คำนวณ U |
| **Outlet (atmosphere)** | `zeroGradient` | `fixedValue` 0 | p = 0 gauge เป็น reference |
| **Outlet (backflow safe)** | `inletOutlet` | `fixedValue` 0 | จัดการ reverse flow |
| **Wall (no-slip)** | `noSlip` | `zeroGradient` | ผนังยึดของไหล |
| **Wall (slip)** | `slip` | `zeroGradient` | ผนัง inviscid (ไม่มีแรงเสียดทาน) |
| **Symmetry** | `symmetry` | `symmetry` | ลดโดเมนครึ่ง |
| **Freestream** | `freestreamVelocity` | `freestreamPressure` | External aero |
| **Moving wall** | `movingWallVelocity` | `zeroGradient` | แถบลำเลียง, ล้อหมุน |
| **Cyclic** | `cyclic` | `cyclic` | Periodic pattern |

---

## Decision Tree

### 1. Inlet: รู้อะไรสำหรับ flow เข้า?

```
รู้ Velocity Profile?
├── ✅ ใช่ → U: fixedValue, p: zeroGradient
│   (ทำไม: กำหนด U แล้ว p จะถูกคำนวณจาก momentum)
│
└── ❌ ไม่ (แต่รู้ Pressure)
    → U: pressureInletVelocity, p: fixedValue
    (ทำไม: กำหนด p แล้วคำนวณ U จาก pressure difference)
```

### 2. Outlet: ไหลออกไปไหน?

```
เป็น Atmosphere?
├── ✅ ใช่ → U: zeroGradient, p: fixedValue 0
│   (ทำไม: p = 0 gauge เป็น reference point)
│
└── ❌ ไม่ → มีโอกาส Backflow?
    ├── ✅ อาจมี → U: inletOutlet, p: fixedValue 0
    │   (ทำไม: zeroGradient + fixedValue ถ้าไหลกลับ)
    │
    └── ❌ ไม่มี → U: zeroGradient, p: fixedValue 0
```

### 3. Wall: ผนังมีพฤติกรรมอย่างไร?

```
ผนังเคลื่อนที่?
├── ✅ ใช่ → U: movingWallVelocity
│   (ทำไม: U ที่ผนัง = ความเร็วผนัง)
│
└── ❌ ไม่ → ต้องการ No-slip?
    ├── ✅ ใช่ (Viscous) → U: noSlip
    │   (ทำไม: ของไหลติดผนัง U = 0)
    │
    └── ❌ ไม่ (Inviscid) → U: slip
        (ทำไม: ไหลขนานผนังได้ แต่ไม่ทะลุ)
```

---

## ตามประเภท Field

### Velocity (U)

| Location | Standard | Alternative | ทำไมใช้ Alternative |
|----------|----------|-------------|---------------------|
| Inlet | `fixedValue` | `pressureInletVelocity` | รู้ p ไม่รู้ U |
| Outlet | `zeroGradient` | `inletOutlet` | ป้องกัน backflow diverge |
| Wall | `noSlip` | `slip`, `movingWallVelocity` | ผนังพิเศษ |
| Freestream | `freestreamVelocity` | — | External aero |

### Pressure (p)

| Location | Standard | Alternative | ทำไมใช้ Alternative |
|----------|----------|-------------|---------------------|
| Inlet | `zeroGradient` | `fixedValue` | Pressure-driven flow |
| Outlet | `fixedValue` | `totalPressure` | รวม dynamic head |
| Wall | `zeroGradient` | `fixedFluxPressure` | Body force (gravity) |
| Freestream | `freestreamPressure` | — | External aero |

### Temperature (T)

| Location | Standard | ทำไม |
|----------|----------|------|
| Inlet | `fixedValue` | รู้ T ของ fluid เข้า |
| Outlet | `zeroGradient` | ปล่อยให้ T ไหลออก |
| Fixed T wall | `fixedValue` | ผนังอุณหภูมิคงที่ |
| Adiabatic wall | `zeroGradient` | ไม่มี heat flux (ฉนวน) |
| Heat flux wall | `fixedGradient` | กำหนด q (W/m²) |
| Convective wall | `mixed` / `externalWallHeatFlux` | h(T_wall - T_ambient) |

### Turbulence (k, ε, ω, nut)

| Location | k | ε | ω | nut |
|----------|---|---|---|-----|
| Inlet | `fixedValue` | `fixedValue` | `fixedValue` | `calculated` |
| Outlet | `zeroGradient` | `zeroGradient` | `zeroGradient` | `calculated` |
| Wall | `kqRWallFunction` | `epsilonWallFunction` | `omegaWallFunction` | `nutkWallFunction` |

**ทำไม Wall ใช้ Wall Function?**
- หลีกเลี่ยง mesh ละเอียดมากใกล้ผนัง
- แต่ต้องมี y+ ในช่วงที่ถูกต้อง (30-300)

---

## Code Examples

### Standard Pipe Flow

```cpp
// 0/U
inlet  { type fixedValue; value uniform (1 0 0); }   // กำหนด U เข้า
outlet { type zeroGradient; }                         // ปล่อยไหลออก
walls  { type noSlip; }                               // ไม่ลื่น

// 0/p
inlet  { type zeroGradient; }                         // ปล่อย p ปรับตัว
outlet { type fixedValue; value uniform 0; }          // Reference p = 0
walls  { type zeroGradient; }                         // ไม่มี p flux
```

### Pressure-Driven Flow

```cpp
// 0/U
inlet  { type pressureInletVelocity; value uniform (0 0 0); }  // คำนวณจาก p
outlet { type zeroGradient; }
walls  { type noSlip; }

// 0/p
inlet  { type fixedValue; value uniform 1000; }   // ความดันสูง
outlet { type fixedValue; value uniform 0; }      // ความดันต่ำ
walls  { type zeroGradient; }
```

### External Aerodynamics

```cpp
// 0/U
freestream { type freestreamVelocity; freestreamValue uniform (50 0 0); }
body       { type noSlip; }

// 0/p
freestream { type freestreamPressure; freestreamValue uniform 0; }
body       { type zeroGradient; }
```

### Heat Transfer

```cpp
// 0/T
inlet       { type fixedValue; value uniform 300; }     // T เข้า
outlet      { type zeroGradient; }                       // ปล่อยไหลออก
hotWall     { type fixedValue; value uniform 400; }     // ผนังร้อน
coldWall    { type fixedValue; value uniform 280; }     // ผนังเย็น
insulated   { type zeroGradient; }                       // ฉนวน

// Convective wall (h = 10 W/m²K, T∞ = 293 K)
convWall
{
    type    externalWallHeatFlux;
    mode    coefficient;
    h       uniform 10;     // W/(m²·K)
    Ta      uniform 293;    // K
}
```

---

## ปัญหาที่พบบ่อย

| ปัญหา | สาเหตุ | ทำไมเกิด | แก้ไข |
|-------|--------|---------|-------|
| Diverge ที่ inlet | U + p fixedValue | Over-constrained | เปลี่ยน p เป็น zeroGradient |
| Backflow ที่ outlet | zeroGradient | ไม่จัดการ reverse flow | ใช้ inletOutlet |
| High velocity ที่ wall | BC type ผิด | ไม่มี no-slip | ใช้ noSlip |
| Pressure drifting | ไม่มี reference | p ไม่มี anchor | fixedValue p ที่ outlet |
| Turbulence ลบ | Wall function + y+ ผิด | y+ ไม่อยู่ในช่วง | ปรับ mesh หรือเปลี่ยน model |

---

## Concept Check

<details>
<summary><b>1. ทำไม inlet ใช้ zeroGradient สำหรับ p?</b></summary>

**เหตุผล:** เพราะเมื่อกำหนด U แล้ว ระบบ "over-constrained" ถ้ากำหนด p ด้วย

- Momentum equation จะคำนวณ p ที่จำเป็นจาก U ที่กำหนด
- `zeroGradient` = ปล่อยให้ p ปรับตัวตามธรรมชาติ (extrapolate จาก internal)

**ตรงข้าม:** Pressure-driven flow กำหนด p แต่ปล่อย U
</details>

<details>
<summary><b>2. inletOutlet ต่างจาก zeroGradient อย่างไร?</b></summary>

| | zeroGradient | inletOutlet |
|-|--------------|-------------|
| Flow ออก | ใช้ internal value | ใช้ internal value (เหมือนกัน) |
| Flow เข้า (backflow) | ยังใช้ internal value (อาจผิด!) | ใช้ `inletValue` ที่กำหนด |

**ทำไมสำคัญ:** Backflow อาจมี velocity ผิด → numerical instability
</details>

<details>
<summary><b>3. ต้องกำหนด reference pressure ที่ไหน? ทำไม?</b></summary>

**ที่ไหน:** **อย่างน้อย 1 จุด** ต้องมี `fixedValue` p — ปกติที่ outlet (p = 0 gauge)

**ทำไม:** สำหรับ incompressible flow, สมการ pressure เป็น Poisson equation:
$$\nabla^2 p = f$$

สมการนี้มีคำตอบ **infinite** (บวก constant ใดๆ ก็ได้) ถ้าไม่มี reference → p สามารถ drift ได้
</details>

<details>
<summary><b>4. fixedFluxPressure ใช้เมื่อไหร่?</b></summary>

**ใช้ที่ผนังเมื่อมี body force (เช่น gravity):**

ปกติ: `∂p/∂n = 0` ที่ผนัง (zeroGradient)

แต่ถ้ามี gravity: `∂p/∂n = ρ g · n`

`fixedFluxPressure` จัดการเรื่องนี้อัตโนมัติ — ใช้กับ buoyant flows
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [02_Fundamental_Classification.md](02_Fundamental_Classification.md) — การจำแนกประเภท
- **บทถัดไป:** [04_Mathematical_Formulation.md](04_Mathematical_Formulation.md) — สูตรทางคณิตศาสตร์
- **Troubleshooting:** [07_Troubleshooting_Boundary_Conditions.md](07_Troubleshooting_Boundary_Conditions.md) — แก้ปัญหา BC