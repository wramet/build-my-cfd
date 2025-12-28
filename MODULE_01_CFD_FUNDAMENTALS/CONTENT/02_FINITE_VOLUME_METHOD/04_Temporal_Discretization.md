# Temporal Discretization

การแปลง $\frac{\partial \phi}{\partial t}$ ให้เป็นสมการพีชคณิตที่แก้ได้ตาม Time Steps

---

## Time Integration Schemes

### 1. Euler (First-Order Implicit)

$$\frac{\phi^{n+1} - \phi^n}{\Delta t} = f(\phi^{n+1})$$

| คุณสมบัติ | ค่า |
|-----------|-----|
| Order | 1st |
| Stability | Unconditionally stable |
| CFL Required | ไม่จำกัด (แต่ accuracy ขึ้นกับ $\Delta t$) |

**OpenFOAM:**
```cpp
ddtSchemes
{
    default     Euler;
}
```

### 2. backward (Second-Order Implicit)

$$\frac{3\phi^{n+1} - 4\phi^n + \phi^{n-1}}{2\Delta t} = f(\phi^{n+1})$$

| คุณสมบัติ | ค่า |
|-----------|-----|
| Order | 2nd |
| Stability | Unconditionally stable |
| เหมาะกับ | ต้องการ temporal accuracy |

**OpenFOAM:**
```cpp
ddtSchemes
{
    default     backward;
}
```

### 3. Crank-Nicolson (Second-Order)

$$\frac{\phi^{n+1} - \phi^n}{\Delta t} = \frac{1}{2}[f(\phi^n) + f(\phi^{n+1})]$$

| คุณสมบัติ | ค่า |
|-----------|-----|
| Order | 2nd |
| Stability | Marginally stable |
| หมายเหตุ | อาจ oscillate ถ้า $\Delta t$ ใหญ่ |

**OpenFOAM:**
```cpp
ddtSchemes
{
    default     CrankNicolson 0.5;  // 0 = Euler, 1 = Pure CN
}
```

---

## Scheme Comparison

| Scheme | Order | Stability | Cost | ใช้เมื่อ |
|--------|-------|-----------|------|---------|
| `Euler` | 1 | ดีมาก | ต่ำ | เริ่มต้น, general |
| `backward` | 2 | ดีมาก | ปานกลาง | ต้องการ accuracy |
| `CrankNicolson` | 2 | ปานกลาง | ปานกลาง | Wave, acoustic |

**คำแนะนำทั่วไป:**
- เริ่มด้วย `Euler` เสมอ
- ถ้า stable แล้วลอง `backward` เพื่อเพิ่ม accuracy
- ใช้ `CrankNicolson` สำหรับ wave propagation

---

## Courant Number (CFL)

$$\text{Co} = \frac{|u| \Delta t}{\Delta x}$$

**ความหมาย:** อัตราส่วนระหว่าง "ระยะที่ของไหลเคลื่อนที่ใน 1 time step" กับ "ขนาด cell"

| Scheme Type | Co Limit |
|-------------|----------|
| Explicit | Co < 1 (บังคับ) |
| Implicit | ไม่จำกัด (แต่ Co > 5 ลด accuracy) |

**ตั้งค่าใน `system/controlDict`:**

```cpp
deltaT          0.001;          // Initial time step
adjustTimeStep  yes;            // Adaptive time stepping
maxCo           0.9;            // Max Courant number
maxAlphaCo      0.5;            // Max Co for phase fraction
maxDeltaT       0.1;            // Max allowed time step
```

---

## Algorithm Selection

| Algorithm | ใช้กับ | ddtScheme | ตั้งค่าใน |
|-----------|--------|-----------|----------|
| **SIMPLE** | Steady-state | ไม่ใช้ ddt | `SIMPLE{}` |
| **PISO** | Transient, Δt เล็ก | `Euler` | `PISO{}` |
| **PIMPLE** | Transient, Δt ใหญ่ | `Euler`/`backward` | `PIMPLE{}` |

### PISO (Transient)

```cpp
PISO
{
    nCorrectors         2;      // Pressure corrections
    nNonOrthogonalCorrectors 1;
}
```

### PIMPLE (Large Δt)

```cpp
PIMPLE
{
    nOuterCorrectors    2;      // Outer loops (SIMPLE-like)
    nCorrectors         1;      // Inner loops (PISO-like)
    nNonOrthogonalCorrectors 1;
}
```

---

## Matrix Contribution

พจน์ $\frac{\partial \phi}{\partial t}$ มีผลต่อ Matrix:

```
[A][φ] = [b]
```

| Component | Euler |
|-----------|-------|
| Diagonal $a_P$ | $+ \frac{\rho V}{\Delta t}$ |
| Source $b_P$ | $+ \frac{\rho V}{\Delta t} \phi^n$ |

**ใน OpenFOAM:**

```cpp
fvScalarMatrix phiEqn
(
    fvm::ddt(rho, phi)        // Implicit temporal (→ diagonal)
  + fvm::div(phi, U)          // Implicit convection (→ diagonal)
  - fvm::laplacian(D, phi)    // Implicit diffusion (→ diagonal)
 ==
    Su                        // Explicit source (→ RHS)
);
```

---

## Best Practices

### 1. เริ่มต้น

```cpp
// system/fvSchemes
ddtSchemes { default Euler; }

// system/controlDict
deltaT          1e-4;
adjustTimeStep  yes;
maxCo           0.5;
```

### 2. หา Steady-State เร็วขึ้น

```cpp
// ใช้ PIMPLE + large Δt
PIMPLE
{
    nOuterCorrectors 50;
    residualControl { p 1e-4; U 1e-4; }
}
```

### 3. Accurate Transient

```cpp
ddtSchemes { default backward; }
maxCo 0.5;  // เพิ่มความแม่นยำ
```

---

## Concept Check

<details>
<summary><b>1. Euler กับ backward ต่างกันอย่างไร?</b></summary>

- **Euler**: 1st order → error $O(\Delta t)$
- **backward**: 2nd order → error $O(\Delta t^2)$
- ทั้งคู่ unconditionally stable แต่ backward แม่นยำกว่า
</details>

<details>
<summary><b>2. ทำไม Co < 1 สำคัญสำหรับ Explicit schemes?</b></summary>

เพราะถ้า Co > 1 หมายความว่าข้อมูลเคลื่อนที่ข้าม cell มากกว่า 1 cell ต่อ time step → information ที่อยู่ระหว่าง cells หายไป → unstable
</details>

<details>
<summary><b>3. PISO กับ PIMPLE ใช้ต่างกันเมื่อไหร่?</b></summary>

- **PISO**: Δt เล็ก, Co < 1, ต้องการ accuracy per time step
- **PIMPLE**: Δt ใหญ่ได้, ใช้ outer loops เพื่อ iterate ให้ converge
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [03_Spatial_Discretization.md](03_Spatial_Discretization.md) — Spatial Discretization
- **บทถัดไป:** [05_Matrix_Assembly.md](05_Matrix_Assembly.md) — Matrix Assembly