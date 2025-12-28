# Lid-Driven Cavity Problem

ฟิสิกส์และคณิตศาสตร์ของ benchmark problem คลาสสิก

---

## Problem Description

กล่องสี่เหลี่ยมบรรจุของไหล ฝาบนเคลื่อนที่ด้วยความเร็วคงที่

```
     Lid (U = 1 m/s →)
    ┌────────────────┐
    │                │
    │    Primary     │
    │    Vortex      │
    │                │
    │  ↙          ↘  │
    │                │
    └────────────────┘
     Wall (no-slip)
```

---

## ทำไมถึงเป็น Benchmark?

1. **Geometry เรียบง่าย** — แค่สี่เหลี่ยม
2. **มี reference solution** — Ghia et al. (1982)
3. **ฟิสิกส์ครบ** — Vortices, boundary layers, shear
4. **Closed system** — ไม่มี inlet/outlet

---

## สมการควบคุม

### Incompressible Navier-Stokes

**Continuity:**
$$\frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} = 0$$

**Momentum (x):**
$$\frac{\partial u}{\partial t} + u\frac{\partial u}{\partial x} + v\frac{\partial u}{\partial y} = -\frac{1}{\rho}\frac{\partial p}{\partial x} + \nu\left(\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2}\right)$$

**Momentum (y):**
$$\frac{\partial v}{\partial t} + u\frac{\partial v}{\partial x} + v\frac{\partial v}{\partial y} = -\frac{1}{\rho}\frac{\partial p}{\partial y} + \nu\left(\frac{\partial^2 v}{\partial x^2} + \frac{\partial^2 v}{\partial y^2}\right)$$

---

## Reynolds Number

$$Re = \frac{UL}{\nu}$$

| Parameter | Symbol | Unit | Typical Value |
|-----------|--------|------|---------------|
| Lid velocity | U | m/s | 1 |
| Cavity length | L | m | 1 |
| Kinematic viscosity | ν | m²/s | 0.01-0.1 |

**ควบคุม Re ด้วย ν:**

```cpp
// constant/transportProperties
nu [0 2 -1 0 0 0 0] 0.1;   // Re = 1×1/0.1 = 10
nu [0 2 -1 0 0 0 0] 0.01;  // Re = 1×1/0.01 = 100
```

---

## Flow Regimes

| Re | Flow Type | Features |
|----|-----------|----------|
| 10 | Laminar, creeping | Single vortex, centered |
| 100 | Laminar | Primary vortex off-center |
| 400 | Laminar | Secondary corner vortices |
| 1000 | Laminar | Multiple corner vortices |
| >2000 | Transitional/Turbulent | Unsteady, 3D effects |

---

## Boundary Conditions

| Boundary | Velocity | Pressure |
|----------|----------|----------|
| Top (lid) | u=U, v=0 | ∂p/∂n=0 |
| Bottom | u=0, v=0 | ∂p/∂n=0 |
| Left | u=0, v=0 | ∂p/∂n=0 |
| Right | u=0, v=0 | ∂p/∂n=0 |

**OpenFOAM implementation:**

```cpp
// 0/U
movingWall  { type fixedValue; value uniform (1 0 0); }
fixedWalls  { type noSlip; }

// 0/p
movingWall  { type zeroGradient; }
fixedWalls  { type zeroGradient; }
```

---

## Flow Features

### Primary Vortex

- ศูนย์กลางอยู่ที่ประมาณ (0.5, 0.4) สำหรับ Re=100
- หมุนตามเข็มนาฬิกา
- ความเข้มขึ้นกับ Re

### Secondary Vortices (Re > 400)

- เกิดที่มุมล่างขวาและล่างซ้าย
- หมุนทวนเวลา
- ขนาดเล็กกว่า primary

### Corner Singularities

- Top corners มี velocity discontinuity
- อาจต้อง mesh refinement

---

## Vortex Center Position (Ghia et al., 1982)

| Re | x/L | y/L |
|----|-----|-----|
| 100 | 0.6172 | 0.7344 |
| 400 | 0.5547 | 0.6055 |
| 1000 | 0.5313 | 0.5625 |

---

## PISO Algorithm

**Pressure Implicit with Splitting of Operators**

```
1. Predict U* (momentum without correct p)
2. Solve pressure Poisson equation
3. Correct U with ∇p'
4. Repeat 2-3 for nCorrectors times
5. Advance to next time step
```

```cpp
// system/fvSolution
PISO
{
    nCorrectors     2;
    pRefCell        0;
    pRefValue       0;
}
```

---

## Mesh Considerations

### Minimum Requirements

| Re | Grid (NxN) | Notes |
|----|------------|-------|
| 10 | 10×10 | Coarse OK |
| 100 | 20×20 | Standard |
| 1000 | 50×50+ | Need refinement |

### Grading

```cpp
// Near-wall refinement
blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 1)
    simpleGrading
    (
        ((0.5 0.5 2)(0.5 0.5 0.5))  // x-direction
        ((0.5 0.5 2)(0.5 0.5 0.5))  // y-direction
        1                            // z-direction
    )
);
```

---

## Concept Check

<details>
<summary><b>1. ทำไม pressure ใช้ zeroGradient ทุกผนัง?</b></summary>

เพราะไม่มี flow ผ่านผนัง (no-slip) → $\mathbf{u} \cdot \mathbf{n} = 0$ → $\frac{\partial p}{\partial n} = 0$ และ reference pressure กำหนดผ่าน pRefCell
</details>

<details>
<summary><b>2. Primary vortex หมุนทิศไหน?</b></summary>

ตามเข็มนาฬิกา — เพราะ lid เคลื่อนที่ไปทางขวา ดึง fluid ไปด้วย แล้ววนกลับมาตาม walls
</details>

<details>
<summary><b>3. ทำไม corner มี velocity discontinuity?</b></summary>

ที่จุดมุมบน: lid มี u=U แต่ wall ข้างมี u=0 → discontinuity → อาจต้อง mesh refinement หรือ special treatment
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [02_The_Workflow.md](02_The_Workflow.md) — Workflow
- **บทถัดไป:** [04_Step-by-Step_Tutorial.md](04_Step-by-Step_Tutorial.md) — Tutorial