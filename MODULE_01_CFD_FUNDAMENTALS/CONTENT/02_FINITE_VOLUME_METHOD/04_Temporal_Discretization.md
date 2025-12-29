# Temporal Discretization

การแปลง $\frac{\partial \phi}{\partial t}$ ให้เป็นสมการพีชคณิตที่แก้ได้ตาม Time Steps

> **ทำไมต้อง discretize เวลา?**
> - คอมพิวเตอร์ไม่เข้าใจ "เวลาต่อเนื่อง" แต่เข้าใจ "ช่วงเวลา"
> - เราเดินจาก $t^n$ ไป $t^{n+1}$ โดยใช้ข้อมูลที่รู้มาแล้ว

---

## Time Integration Schemes

### 1. Euler (First-Order Implicit)

$$\frac{\phi^{n+1} - \phi^n}{\Delta t} = f(\phi^{n+1})$$

> **💡 คิดแบบนี้:**
> "ถามอนาคตว่าจะเป็นอย่างไร แล้วใช้คำตอบนั้นมาคำนวณ"
> → ต้องแก้สมการ implicit (มี unknown ทั้งสองฝั่ง)

| คุณสมบัติ | ค่า | ทำไม |
|-----------|-----|------|
| Order | 1st | ใช้แค่ 2 time levels |
| Stability | Unconditionally stable | RHS ใช้ค่าที่ $t^{n+1}$ (ยังไม่เกิด oscillation) |
| Cost | ต่ำ | แก้ matrix ครั้งเดียวต่อ time step |

**OpenFOAM:**
```cpp
ddtSchemes
{
    default     Euler;
}
```

**ใช้เมื่อ:**
- เริ่มต้น simulation ใหม่
- ต้องการความเสถียร ไม่เน้น temporal accuracy

---

### 2. backward (Second-Order Implicit)

$$\frac{3\phi^{n+1} - 4\phi^n + \phi^{n-1}}{2\Delta t} = f(\phi^{n+1})$$

> **💡 คิดแบบนี้:**
> ใช้ 3 time levels (อดีต + ปัจจุบัน + อนาคต) ทำให้ "เดา" อนาคตแม่นยำขึ้น

| คุณสมบัติ | ค่า | ทำไม |
|-----------|-----|------|
| Order | 2nd | ใช้ 3 time levels |
| Stability | Unconditionally stable | Still implicit |
| Memory | ต้องเก็บ $\phi^{n-1}$ | เพิ่ม memory usage |

**OpenFOAM:**
```cpp
ddtSchemes
{
    default     backward;
}
```

**ใช้เมื่อ:**
- ต้องการ temporal accuracy (vortex shedding, acoustic)
- **หลังจาก** simulation stable แล้วด้วย Euler

---

### 3. Crank-Nicolson (Second-Order)

$$\frac{\phi^{n+1} - \phi^n}{\Delta t} = \frac{1}{2}[f(\phi^n) + f(\phi^{n+1})]$$

> **💡 คิดแบบนี้:**
> เฉลี่ย RHS จากอดีตและอนาคต → "ยุติธรรม" กับทั้งสอง

### Crank-Nicolson Coefficient Blending

ใน OpenFOAM เราสามารถ blend ระหว่าง Euler และ Pure Crank-Nicolson:

$$\text{RHS} = (1-\theta) \cdot f(\phi^n) + \theta \cdot f(\phi^{n+1})$$

โดยที่:
- $\theta = 0$ → **Euler implicit** (most stable, least accurate)
- $\theta = 0.5$ → **Pure Crank-Nicolson** (2nd order, marginally stable)
- $\theta = 1$ → ไม่ใช้ (ไม่มี implicit part)

**ใน OpenFOAM:**
```cpp
ddtSchemes
{
    default     CrankNicolson 0.5;  // θ = 0.5 (Pure CN)
    // หรือ
    default     CrankNicolson 0.9;  // θ = 0.9 (more stable than 0.5)
    // หรือ
    default     Euler;              // θ → 0 (most stable)
}
```

**การเลือกค่า θ:**

| θ Value | ความเสถียร | ความแม่นยำ | ใช้เมื่อ |
|---------|-----------|-----------|----------|
| **0.3 - 0.5** | ต่ำ | สูง (2nd order) | Acoustics, waves ที่ไม่มี shocks |
| **0.7 - 0.9** | ปานกลาง-สูง | ปานกลาง-สูง | General transient, balance |
| **1.0** | เป็น Euler | 1st order | Startup, ไม่ต้องการ accuracy |

| คุณสมบัติ | ค่า | ทำไม |
|-----------|-----|------|
| Order | 2nd | เฉลี่ย explicit + implicit |
| Stability | Marginally stable | อาจ oscillate ถ้า $\Delta t$ ใหญ่ |
| ใช้กับ | Wave propagation | เก็บ energy ดี |

**ใช้เมื่อ:**
- Wave propagation (acoustic, surface waves)
- ต้องการ energy conservation

---

## Scheme Comparison

| Scheme | Order | Stability | Cost | ใช้เมื่อ |
|--------|-------|-----------|------|---------|
| `Euler` | 1 | ดีมาก | ต่ำ | เริ่มต้น, general |
| `backward` | 2 | ดีมาก | ปานกลาง | ต้องการ accuracy |
| `CrankNicolson` | 2 | ปานกลาง | ปานกลาง | Wave, acoustic |

**คำแนะนำ:**

```
เริ่มต้น → Euler (stable)
    ↓
Stable แล้ว → backward (accurate)
    ↓
Wave problems → CrankNicolson 0.5-0.9
```

---

## Courant Number (CFL)

$$\text{Co} = \frac{\|\mathbf{u}\| \Delta t}{\Delta x} \quad \text{(1D)}$$

**สำหรับ 3D:**
$$\text{Co} = \frac{\max(\|\mathbf{u}\|) \Delta t}{\min(\Delta x, \Delta y, \Delta z)}$$

> **ความหมายทางกายภาพ:**
> Co = "จำนวน cells ที่ข้อมูลเดินทางได้ใน 1 time step"
>
> - Co = 0.5 → ข้อมูลเดินทางครึ่ง cell
> - Co = 1 → ข้อมูลเดินทางพอดี 1 cell
> - Co = 2 → ข้อมูลกระโดดข้าม 2 cells (อันตราย!)

### ทำไม CFL สำคัญ?

| Scheme Type | Co Limit | ผลถ้าเกิน |
|-------------|----------|----------|
| Explicit | **Co < 1** (บังคับ) | Blow up ทันที |
| Implicit | ไม่จำกัด | Accuracy ลดลงมาก |

**ตั้งค่าใน `system/controlDict`:**

```cpp
deltaT          0.001;          // Initial time step
adjustTimeStep  yes;            // ปรับ Δt อัตโนมัติตาม Co
maxCo           0.9;            // เป้าหมาย Co สูงสุด
maxAlphaCo      0.5;            // Co สำหรับ phase fraction (VOF)
maxDeltaT       0.1;            // จำกัด Δt ไม่ให้ใหญ่เกิน
```

**ทำไมใช้ maxCo < 1?**
- ให้ margin of safety
- physics อาจเปลี่ยนเร็ว → Co กระโดดได้

---

## Algorithm Selection

| Algorithm | ใช้กับ | Temporal | ตั้งค่าใน |
|-----------|--------|----------|----------|
| **SIMPLE** | Steady-state | ไม่ใช้ ddt | `SIMPLE{}` |
| **PISO** | Transient, Δt เล็ก | Euler | `PISO{}` |
| **PIMPLE** | Transient, Δt ใหญ่ | Euler/backward | `PIMPLE{}` |

### PISO (Pressure Implicit with Splitting of Operators)

```cpp
PISO
{
    nCorrectors         2;      // วน pressure correction กี่รอบ
    nNonOrthogonalCorrectors 1; // แก้ mesh เบี้ยว
}
```

**ทำไม nCorrectors = 2?**
- 1 รอบ: ประมาณ 85% converge
- 2 รอบ: ประมาณ 98% converge
- 3+ รอบ: เพิ่ม cost ไม่คุ้ม

### PIMPLE (PISO + SIMPLE)

```cpp
PIMPLE
{
    nOuterCorrectors    2;      // Outer loops = เหมือน SIMPLE
    nCorrectors         1;      // Inner loops = เหมือน PISO
    nNonOrthogonalCorrectors 1;
}
```

**ทำไมใช้ PIMPLE?**
- PISO: ต้อง Co < 1 → Δt เล็ก → ช้า
- PIMPLE: Co > 1 ได้ → Δt ใหญ่ → เร็วขึ้น (แต่วนรอบมากขึ้น)

---

## Matrix Contribution

พจน์ $\frac{\partial \phi}{\partial t}$ มีผลต่อ Matrix:

| Component | Euler | ความหมาย |
|-----------|-------|----------|
| Diagonal $a_P$ | $+ \frac{\rho V}{\Delta t}$ | ทำให้ diagonal dominant (stable) |
| Source $b_P$ | $+ \frac{\rho V}{\Delta t} \phi^n$ | นำค่าเก่ามาใช้ |

**ใน OpenFOAM:**

```cpp
fvScalarMatrix phiEqn
(
    fvm::ddt(rho, phi)        // → เพิ่ม diagonal + source
  + fvm::div(phi, U)          // → เพิ่ม diagonal + off-diagonal
  - fvm::laplacian(D, phi)    // → เพิ่ม diagonal + off-diagonal
 ==
    Su                        // → explicit source (→ RHS)
);
```

---

## Best Practices

### 1. เริ่มต้น (Safe Start)

```cpp
// system/fvSchemes
ddtSchemes { default Euler; }

// system/controlDict
deltaT          1e-4;
adjustTimeStep  yes;
maxCo           0.5;    // Conservative
```

### 2. เร่งหา Steady-State

```cpp
// ใช้ PIMPLE + large Δt + many outer
PIMPLE
{
    nOuterCorrectors 50;
    residualControl { p 1e-4; U 1e-4; }
}
```

**ทำไมได้ผล?** PIMPLE + many outer = SIMPLE-like behavior → ไม่สน time accuracy แต่ converge เร็ว

### 3. Accurate Transient

```cpp
ddtSchemes { default backward; }
maxCo 0.5;  // ลด Co เพื่อเพิ่มความแม่นยำ
```

---

## Concept Check

<details>
<summary><b>1. Euler กับ backward ต่างกันอย่างไร? ควรใช้เมื่อไหร่?</b></summary>

| | Euler | backward |
|-|-------|----------|
| Order | 1st | 2nd |
| Error | $O(\Delta t)$ | $O(\Delta t^2)$ |
| Memory | เก็บแค่ $\phi^n$ | ต้องเก็บ $\phi^{n-1}$ ด้วย |
| ใช้เมื่อ | เริ่มต้น, general | ต้องการ temporal accuracy |

**ข้อควรระวัง:** หลีกเลี่ยง backward ตอนเริ่มต้น — รอให้ stable ก่อน
</details>

<details>
<summary><b>2. ทำไม Co < 1 สำคัญสำหรับ Explicit schemes?</b></summary>

**ตอบ:** เพราะ explicit scheme ใช้แต่ข้อมูลจาก $t^n$ เท่านั้น

ถ้า Co > 1 → ข้อมูลจริง "เดินทาง" ข้ามหลาย cells
แต่ scheme "มองเห็น" แค่ neighboring cells
→ **พลาดข้อมูลสำคัญ** → unstable

**เปรียบเทียบ:** เหมือนขับรถเร็วมากจนมองไม่เห็นป้ายจราจร
</details>

<details>
<summary><b>3. PISO กับ PIMPLE ใช้ต่างกันเมื่อไหร่?</b></summary>

| | PISO | PIMPLE |
|-|------|--------|
| Co | ต้อง < 1 | ได้ > 1 |
| Outer loops | ไม่มี | มี (nOuterCorrectors) |
| ใช้เมื่อ | ต้องการ accuracy ต่อ time step | ต้องการความเร็ว, large Δt |

**Rule of thumb:**
- ถ้า physics ต้อง resolve ทุก time step (acoustic, FSI) → PISO
- ถ้าสนแค่ final result หรือ quasi-steady → PIMPLE + large Δt
</details>

<details>
<summary><b>4. CrankNicolson 0.5 หมายความว่าอะไร?</b></summary>

**ตอบ:** Blending factor ระหว่าง Euler (0) และ Pure CN (1)

$$\phi^{n+1} = (1-\theta) \cdot \text{Euler} + \theta \cdot \text{CrankNicolson}$$

- `CrankNicolson 0` = Euler (most stable)
- `CrankNicolson 1` = Pure CN (may oscillate)
- `CrankNicolson 0.5` = Compromise

**ใช้ 0.9:** ต้องการ CN accuracy แต่ลดโอกาส oscillation
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [03_Spatial_Discretization.md](03_Spatial_Discretization.md) — Spatial Discretization
- **บทถัดไป:** [05_Matrix_Assembly.md](05_Matrix_Assembly.md) — Matrix Assembly
- **ประยุกต์:** [07_Best_Practices.md](07_Best_Practices.md) — Best Practices