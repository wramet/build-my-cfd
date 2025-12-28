# Lid-Driven Cavity Problem

ฟิสิกส์และคณิตศาสตร์ของ benchmark problem คลาสสิก

> **ทำไม Lid-Driven Cavity สำคัญ?**
> - เป็น **benchmark problem อันดับหนึ่ง** สำหรับ CFD validation
> - ง่ายพอที่จะเข้าใจ แต่ซับซ้อนพอที่จะท้าทาย
> - มี reference solution ที่เชื่อถือได้ (Ghia et al., 1982)
> - ฟิสิกส์ครบ: vortices, boundary layers, shear, separation

---

## Problem Description

กล่องสี่เหลี่ยมบรรจุของไหล ฝาบนเคลื่อนที่ด้วยความเร็วคงที่

```
     Lid (U = 1 m/s →)
    ┌────────────────┐
    │                │
    │    Primary     │
    │    Vortex      │
    │       ↻        │
    │                │
    │  ↙          ↘  │
    │                │
    └────────────────┘
     Wall (no-slip)
```

> **💡 คิดแบบนี้:**
> เหมือนใช้ฝามือปัดผิวน้ำในอ่าง — น้ำจะหมุนวนตามแรงปัด

---

## ทำไมถึงเป็น Benchmark?

1. **Geometry เรียบง่าย** — แค่สี่เหลี่ยม ไม่มี geometric complexity
2. **มี reference solution** — Ghia et al. (1982) ได้รับการ cite มากกว่า 10,000 ครั้ง
3. **ฟิสิกส์ครบ** — Vortices, boundary layers, shear, corner flows
4. **Closed system** — ไม่มี inlet/outlet → ไม่ต้องกังวลเรื่อง inflow/outflow BCs
5. **Scalable difficulty** — เพิ่ม Re = เพิ่มความยาก

---

## สมการควบคุม

### Incompressible Navier-Stokes

**Continuity (2D):**
$$\frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} = 0$$

**ความหมาย:** มวลอนุรักษ์ — สิ่งที่ไหลเข้าต้องไหลออก

**Momentum (x-direction):**
$$\underbrace{\frac{\partial u}{\partial t}}_{\text{local acc.}} + \underbrace{u\frac{\partial u}{\partial x} + v\frac{\partial u}{\partial y}}_{\text{convection}} = \underbrace{-\frac{1}{\rho}\frac{\partial p}{\partial x}}_{\text{pressure}} + \underbrace{\nu\left(\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2}\right)}_{\text{viscous}}$$

**Momentum (y-direction):**
$$\frac{\partial v}{\partial t} + u\frac{\partial v}{\partial x} + v\frac{\partial v}{\partial y} = -\frac{1}{\rho}\frac{\partial p}{\partial y} + \nu\left(\frac{\partial^2 v}{\partial x^2} + \frac{\partial^2 v}{\partial y^2}\right)$$

---

## Reynolds Number

$$Re = \frac{UL}{\nu} = \frac{\text{Inertial forces}}{\text{Viscous forces}}$$

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
nu [0 2 -1 0 0 0 0] 0.001; // Re = 1×1/0.001 = 1000
```

**ทำไมเปลี่ยน ν ไม่เปลี่ยน U?**
- รักษา U = 1 m/s ทำให้ non-dimensionalization ง่าย
- ผลลัพธ์เปรียบเทียบกับ Ghia ได้ตรงๆ

---

## Flow Regimes

| Re | Flow Type | Features | Physics |
|----|-----------|----------|---------|
| 10 | Laminar, creeping | Single vortex, centered | Viscous dominated |
| 100 | Laminar | Primary vortex off-center | Balance viscous/inertia |
| 400 | Laminar | Secondary corner vortices | Separation begins |
| 1000 | Laminar | Multiple corner vortices | Strong separation |
| >2000 | Transitional/Turbulent | Unsteady, 3D effects | Inertia dominated |

**ทำไม Re สูงขึ้น = ซับซ้อนขึ้น?**
- Re สูง → inertia ชนะ viscosity
- ของไหล "ไม่ยอม" เลี้ยวอย่างนุ่มนวล → separation
- เกิด secondary vortices, instabilities

---

## Boundary Conditions

| Boundary | Velocity | Pressure | ทำไม |
|----------|----------|----------|------|
| Top (lid) | u=U, v=0 | ∂p/∂n=0 | ฝาเคลื่อนที่ |
| Bottom | u=0, v=0 | ∂p/∂n=0 | ผนังนิ่ง |
| Left | u=0, v=0 | ∂p/∂n=0 | ผนังนิ่ง |
| Right | u=0, v=0 | ∂p/∂n=0 | ผนังนิ่ง |

**ทำไม p ใช้ zeroGradient ทุกผนัง?**
- ไม่มี flow ผ่านผนัง (no-slip) → $\mathbf{u} \cdot \mathbf{n} = 0$
- No-penetration → $\frac{\partial p}{\partial n} ≈ 0$ (from NS equation at wall)
- Reference pressure กำหนดผ่าน `pRefCell`

**OpenFOAM implementation:**

```cpp
// 0/U
movingWall  { type fixedValue; value uniform (1 0 0); }  // Lid
fixedWalls  { type noSlip; }                              // Other walls

// 0/p
movingWall  { type zeroGradient; }
fixedWalls  { type zeroGradient; }
```

---

## Flow Features

### Primary Vortex

- ศูนย์กลางอยู่ที่ประมาณ (0.5, 0.4-0.7) ขึ้นกับ Re
- หมุน **ตามเข็มนาฬิกา** (lid ดึงของไหลไปขวา)
- ความเข้ม (circulation) เพิ่มขึ้นตาม Re

### Secondary Vortices (Re > 400)

- เกิดที่ **มุมล่างขวาและล่างซ้าย**
- หมุน **ทวนเวลา** (opposite to primary)
- ขนาดเล็กกว่า primary มาก

**ทำไมเกิด secondary vortices?**
- Primary vortex "ดัน" ของไหลเข้ามุม
- ของไหลไม่มีที่ไป → หมุนวนในมุม

### Corner Singularities

- Top corners มี **velocity discontinuity**
- Lid: u = U, แต่ wall ข้าง: u = 0
- จุดมุมเป็น singular point (mathematically ill-defined)
- **ปัญหาจริง:** ต้อง mesh refinement หรือ special treatment

---

## Vortex Center Position (Reference: Ghia et al., 1982)

| Re | x/L | y/L |
|----|-----|-----|
| 100 | 0.6172 | 0.7344 |
| 400 | 0.5547 | 0.6055 |
| 1000 | 0.5313 | 0.5625 |

**ใช้ตรวจสอบ simulation:**
1. หา vortex center จากผลลัพธ์
2. เปรียบเทียบกับ Ghia
3. ใกล้เคียง = mesh/settings ถูกต้อง

---

## PISO Algorithm

**Pressure Implicit with Splitting of Operators**

> **ทำไมใช้ PISO?**
> - ปัญหา transient → ต้องการ accuracy ทุก time step
> - PISO แก้ p หลายครั้งต่อ time step → U และ p consistent

```
1. Predict U* (momentum without correct p)
2. Solve pressure Poisson equation for p'
3. Correct U = U* - ∇p'/A
4. Repeat 2-3 for nCorrectors times
5. Advance to next time step
```

```cpp
// system/fvSolution
PISO
{
    nCorrectors     2;          // จำนวน pressure corrections
    pRefCell        0;          // Cell ที่ fix reference p
    pRefValue       0;          // ค่า reference p
}
```

**ทำไม pRefCell/pRefValue สำคัญ?**
- No fixedValue p BC → p ไม่มี anchor
- ต้องกำหนด reference point → pressure unique

---

## Mesh Considerations

### Minimum Requirements

| Re | Grid (NxN) | Notes |
|----|------------|-------|
| 10 | 10×10 | Coarse OK (viscous dominated) |
| 100 | 20×20 | Standard validation |
| 1000 | 50×50+ | Need refinement near walls |

**ทำไม Re สูงต้อง mesh ละเอียดกว่า?**
- Re สูง → boundary layer บางลง
- ต้อง resolve thin layers ใกล้ผนัง

### Grading (Near-Wall Refinement)

```cpp
// Near-wall refinement
blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 1)
    simpleGrading
    (
        ((0.5 0.5 2)(0.5 0.5 0.5))  // x: กลางหยาบ ขอบละเอียด
        ((0.5 0.5 2)(0.5 0.5 0.5))  // y: กลางหยาบ ขอบละเอียด
        1                            // z: uniform (2D)
    )
);
```

---

## Mesh Independence Study

> **ทำไมสำคัญ?**
> - ผลลัพธ์ต้อง "ไม่ขึ้นกับ mesh"
> - ถ้า refine แล้วผลเปลี่ยน = mesh หยาบเกินไป

**วิธีทำ:**
1. รัน 20×20, 40×40, 80×80
2. เปรียบเทียบ vortex center position
3. ถ้าต่างกัน < 1% = mesh independent

---

## Concept Check

<details>
<summary><b>1. ทำไม pressure ใช้ zeroGradient ทุกผนัง?</b></summary>

**เหตุผล:**
- No-slip wall: $\mathbf{u} = 0$ → no flow through wall
- จาก NS equation ที่ผนัง: $\frac{\partial p}{\partial n} ≈ 0$
- **แต่** ไม่มี fixedValue p เลย → ต้องใช้ `pRefCell` เป็น reference

**สรุป:** Closed cavity ไม่มี outlet → p ต้อง anchor ด้วย pRefCell
</details>

<details>
<summary><b>2. Primary vortex หมุนทิศไหน? ทำไม?</b></summary>

**ตามเข็มนาฬิกา** (clockwise)

**เหตุผล:**
1. Lid เคลื่อนที่ไปทางขวา → ดึง fluid ไปด้วย
2. Fluid ไปชนผนังขวา → ถูกบังคับไหลลง
3. ไหลลงไปชนพื้น → ถูกบังคับไหลซ้าย
4. ไหลซ้ายไปชนผนังซ้าย → ถูกบังคับไหลขึ้น
5. กลับมาที่ lid → วนซ้ำ
</details>

<details>
<summary><b>3. ทำไม corner มี velocity discontinuity?</b></summary>

**ปัญหาที่มุมบน:**
- Lid (top): u = U (เคลื่อนที่)
- Wall (side): u = 0 (นิ่ง)
- **ที่จุดมุม:** ทั้งสอง BC ขัดแย้งกัน!

**ผลกระทบ:**
- Mathematically: singular point
- Numerically: อาจมี artifacts ถ้า mesh หยาบ
- **แก้ไข:** Mesh refinement ที่มุม หรือ smooth transition
</details>

<details>
<summary><b>4. ทำไม PISO ใช้ nCorrectors = 2?</b></summary>

**เหตุผล:**
- 1 correction: ~85% accurate
- 2 corrections: ~98% accurate
- 3+ corrections: เพิ่มน้อยมาก ไม่คุ้มค่า cost

**สำหรับ cavity:**
- Flow relatively simple
- nCorrectors = 2 เพียงพอ
- Highly transient/complex อาจต้อง 3
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [02_The_Workflow.md](02_The_Workflow.md) — Workflow
- **บทถัดไป:** [04_Step-by-Step_Tutorial.md](04_Step-by-Step_Tutorial.md) — Tutorial
- **Reference:** Ghia, U., Ghia, K. N., & Shin, C. T. (1982). High-Re solutions for incompressible flow using the Navier-Stokes equations and a multigrid method. *Journal of Computational Physics*, 48(3), 387-411.