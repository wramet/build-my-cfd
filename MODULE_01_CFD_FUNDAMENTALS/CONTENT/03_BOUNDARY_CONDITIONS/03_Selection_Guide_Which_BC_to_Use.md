# คู่มือการเลือก Boundary Condition

Decision guide สำหรับเลือก BC ที่เหมาะสมกับแต่ละสถานการณ์

---

## Quick Reference Table

| สถานการณ์ | Velocity (U) | Pressure (p) | หมายเหตุ |
|-----------|-------------|--------------|----------|
| **Velocity inlet** | `fixedValue` | `zeroGradient` | กำหนด U, ปล่อย p |
| **Pressure inlet** | `pressureInletVelocity` | `fixedValue` | กำหนด p, คำนวณ U |
| **Outlet (atmosphere)** | `zeroGradient` | `fixedValue` 0 | p = 0 gauge |
| **Outlet (backflow safe)** | `inletOutlet` | `fixedValue` 0 | จัดการ backflow |
| **Wall (no-slip)** | `noSlip` | `zeroGradient` | ผนังแข็ง |
| **Wall (slip)** | `slip` | `zeroGradient` | ผนัง inviscid |
| **Symmetry** | `symmetry` | `symmetry` | ลดโดเมนครึ่ง |
| **Freestream** | `freestreamVelocity` | `freestreamPressure` | External aero |
| **Moving wall** | `movingWallVelocity` | `zeroGradient` | แถบลำเลียง |
| **Cyclic** | `cyclic` | `cyclic` | Periodic |

---

## Decision Tree

### 1. Inlet

```
รู้ Velocity Profile?
├── ใช่ → U: fixedValue, p: zeroGradient
└── ไม่ (รู้ Pressure) → U: pressureInletVelocity, p: fixedValue
```

### 2. Outlet

```
เป็น Atmosphere?
├── ใช่ → U: zeroGradient, p: fixedValue 0
└── ไม่ → มี Backflow?
    ├── อาจมี → U: inletOutlet, p: fixedValue 0
    └── ไม่มี → U: zeroGradient, p: fixedValue 0
```

### 3. Wall

```
ผนังเคลื่อนที่?
├── ใช่ → U: movingWallVelocity
└── ไม่ → ต้องการ No-slip?
    ├── ใช่ → U: noSlip
    └── ไม่ (Inviscid) → U: slip
```

---

## ตามประเภท Field

### Velocity (U)

| Location | Standard | Alternative |
|----------|----------|-------------|
| Inlet | `fixedValue` | `pressureInletVelocity` |
| Outlet | `zeroGradient` | `inletOutlet`, `pressureInletOutletVelocity` |
| Wall | `noSlip` | `slip`, `movingWallVelocity` |
| Freestream | `freestreamVelocity` | — |

### Pressure (p)

| Location | Standard | Alternative |
|----------|----------|-------------|
| Inlet | `zeroGradient` | `fixedValue` (pressure-driven) |
| Outlet | `fixedValue` | `totalPressure` |
| Wall | `zeroGradient` | `fixedFluxPressure` |
| Freestream | `freestreamPressure` | — |

### Temperature (T)

| Location | Standard | Alternative |
|----------|----------|-------------|
| Inlet | `fixedValue` | `zeroGradient` (adiabatic) |
| Outlet | `zeroGradient` | `inletOutlet` |
| Fixed T wall | `fixedValue` | — |
| Adiabatic wall | `zeroGradient` | — |
| Heat flux wall | `fixedGradient` | `externalWallHeatFlux` |
| Convective wall | `mixed` | `externalWallHeatFlux` |

### Turbulence (k, ε, ω, nut)

| Location | k | ε | ω | nut |
|----------|---|---|---|-----|
| Inlet | `fixedValue` | `fixedValue` | `fixedValue` | `calculated` |
| Outlet | `zeroGradient` | `zeroGradient` | `zeroGradient` | `calculated` |
| Wall | `kqRWallFunction` | `epsilonWallFunction` | `omegaWallFunction` | `nutkWallFunction` |

---

## Code Examples

### Standard Pipe Flow

```cpp
// 0/U
inlet  { type fixedValue; value uniform (1 0 0); }
outlet { type zeroGradient; }
walls  { type noSlip; }

// 0/p
inlet  { type zeroGradient; }
outlet { type fixedValue; value uniform 0; }
walls  { type zeroGradient; }
```

### Pressure-Driven Flow

```cpp
// 0/U
inlet  { type pressureInletVelocity; value uniform (0 0 0); }
outlet { type zeroGradient; }
walls  { type noSlip; }

// 0/p
inlet  { type fixedValue; value uniform 1000; }  // Pa
outlet { type fixedValue; value uniform 0; }
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
inlet       { type fixedValue; value uniform 300; }
outlet      { type zeroGradient; }
hotWall     { type fixedValue; value uniform 400; }
coldWall    { type fixedValue; value uniform 280; }
insulated   { type zeroGradient; }

// Convective wall
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

| ปัญหา | สาเหตุ | แก้ไข |
|-------|--------|-------|
| Diverge ที่ inlet | U fixedValue + p fixedValue | เปลี่ยน p เป็น zeroGradient |
| Backflow ที่ outlet | zeroGradient ไม่จัดการ reverse flow | ใช้ inletOutlet |
| High velocity ที่ wall | BC type ผิด | ใช้ noSlip |
| Pressure drifting | ไม่มี reference p | fixedValue p ที่ outlet |

---

## Concept Check

<details>
<summary><b>1. ทำไม inlet ใช้ zeroGradient สำหรับ p?</b></summary>

เพราะเมื่อกำหนด U แล้ว p จะถูกคำนวณจาก momentum equation → ปล่อยให้ p ปรับตัวตามธรรมชาติ
</details>

<details>
<summary><b>2. inletOutlet ต่างจาก zeroGradient อย่างไร?</b></summary>

- `zeroGradient`: ใช้ค่าจาก internal field เสมอ
- `inletOutlet`: ถ้า flow ออก → zeroGradient, ถ้า flow กลับเข้า → ใช้ `inletValue`
</details>

<details>
<summary><b>3. ต้องกำหนด reference pressure ที่ไหน?</b></summary>

อย่างน้อย 1 จุด ต้องมี `fixedValue` p — ปกติที่ outlet (p = 0 gauge)
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [02_Fundamental_Classification.md](02_Fundamental_Classification.md) — การจำแนกประเภท
- **บทถัดไป:** [04_Mathematical_Formulation.md](04_Mathematical_Formulation.md) — สูตรทางคณิตศาสตร์