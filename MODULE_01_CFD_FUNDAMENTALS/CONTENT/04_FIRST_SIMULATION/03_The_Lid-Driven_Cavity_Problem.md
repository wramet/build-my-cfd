# Lid-Driven Cavity Problem

ฟิสิกส์และคณิตศาสตร์ของ benchmark problem คลาสสิก

## Learning Objectives

หลังจากศึกษาบทนี้ คุณควรจะสามารถ:
- **อธิบาย** ทำไม Lid-Driven Cavity เป็น benchmark problem อันดับหนึ่งสำหรับ CFD validation
- **เข้าใจ** ฟิสิกส์ของปัญหานี้: primary vortex, secondary vortices, boundary layers
- **วิเคราะห์** ผลกระทบของ Reynolds number ต่อ flow regimes และ flow features
- **ตั้งค่า** boundary conditions ที่เหมาะสมสำหรับ closed cavity problem
- **ออกแบบ** mesh ที่เหมาะสมกับ Reynolds number ที่ต่างกัน รวมถึง grading syntax
- **ทำความเข้าใจ** สมการ Navier-Stokes สำหรับ incompressible flow (WHAT และ HOW)

> **ทำไม Lid-Driven Cavity สำคัญ?**
> - เป็น **benchmark problem อันดับหนึ่ง** สำหรับ CFD validation
> - ง่ายพอที่จะเข้าใจ แต่ซับซ้อนพอที่จะท้าทาย
> - มี reference solution ที่เชื่อถือได้ (Ghia et al., 1982)
> - ฟิสิกส์ครบ: vortices, boundary layers, shear, separation

---

## Problem Description

**WHAT:** กล่องสี่เหลี่ยมบรรจุของไหล ฝาบนเคลื่อนที่ด้วยความเร็วคงที่

**WHY:** เป็นรูปทรงเรขาคณิตที่เรียบง่ายที่สุด แต่สร้าง flow patterns ที่ซับซ้อนเพียงพอที่จะทดสอบความสามารถของ CFD solver

**HOW:**
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

### WHAT — Five Key Advantages

1. **Geometry เรียบง่าย** — แค่สี่เหลี่ยม ไม่มี geometric complexity
2. **มี reference solution** — Ghia et al. (1982) ได้รับการ cite มากกว่า 10,000 ครั้ง
3. **ฟิสิกส์ครบ** — Vortices, boundary layers, shear, corner flows
4. **Closed system** — ไม่มี inlet/outlet → ไม่ต้องกังวลเรื่อง inflow/outflow BCs
5. **Scalable difficulty** — เพิ่ม Re = เพิ่มความยาก

### WHY — ทำถูกต้อง = เชื่อถือได้

Reference solution จาก Ghia et al. (1982) ใช้ multigrid method ที่มีความละเอียดสูงมาก (129×129 grid สำหรับ Re=1000) ทำให้เป็นมาตรฐานสากลสำหรับ validation

### HOW — การใช้งานจริง

```bash
# เปรียบเทียบผลลัพธ์กับ Ghia
# 1. Extract velocity profile ตามแนวกลาง
# 2. Plot u-velocity ตาม y/L ที่ x/L = 0.5
# 3. Plot v-velocity ตาม x/L ที่ y/L = 0.5
# 4. เปรียบเทียบ vortex center position
```

---

## สมการควบคุม

### WHAT — Governing Equations สำหรับ Incompressible Flow

#### Continuity Equation (Mass Conservation)

**Equation:**
$$\frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} = 0$$

**WHAT:** สมการที่รับประกันว่ามวลอนุรักษ์ — สิ่งที่ไหลเข้าต้องไหลออกเท่ากัน

**WHY:** สำหรับ incompressible flow (ความหนาแน่นคงที่) การอนุรักษ์มวลจึงเทียบเท่ากับ volume flow rate ต้องสมดุล

**HOW:** ใน numerical method สมการนี้ใช้เพื่อ derive pressure Poisson equation ที่ใช้แก้ปัญหา pressure-velocity coupling

---

### Momentum Equations (Newton's Second Law for Fluid)

**WHAT:** สมการที่อธิบายการเปลี่ยนแปลงของโมเมนตัมของของไหล ซึ่งเป็นผลรวมของแรงทั้งหมดที่กระทำต่อของไหล

**Momentum (x-direction):**
$$\underbrace{\frac{\partial u}{\partial t}}_{\text{local acc.}} + \underbrace{u\frac{\partial u}{\partial x} + v\frac{\partial u}{\partial y}}_{\text{convection}} = \underbrace{-\frac{1}{\rho}\frac{\partial p}{\partial x}}_{\text{pressure}} + \underbrace{\nu\left(\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2}\right)}_{\text{viscous}}$$

**Momentum (y-direction):**
$$\underbrace{\frac{\partial v}{\partial t}}_{\text{local acc.}} + \underbrace{u\frac{\partial v}{\partial x} + v\frac{\partial v}{\partial y}}_{\text{convection}} = \underbrace{-\frac{1}{\rho}\frac{\partial p}{\partial y}}_{\text{pressure}} + \underbrace{\nu\left(\frac{\partial^2 v}{\partial x^2} + \frac{\partial^2 v}{\partial y^2}\right)}_{\text{viscous}}$$

**HOW — แต่ละ term ทำหน้าที่อะไร:**

| Term | Mathematical Form | Physical Meaning |
|------|-------------------|------------------|
| **Local Acceleration** | $\frac{\partial u}{\partial t}$ | เวลาเท่ากัน → velocity เปลี่ยน (unsteady) |
| **Convective Acceleration** | $u\frac{\partial u}{\partial x} + v\frac{\partial u}{\partial y}$ | ของไหลเคลื่อนที่ → velocity เปลี่ยน (nonlinear!) |
| **Pressure Gradient** | $-\frac{1}{\rho}\frac{\partial p}{\partial x}$ | ความดันสูงไปต่ำ → ดันของไหล |
| **Viscous Diffusion** | $\nu\left(\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2}\right)$ | ความหนืด → ลด velocity gradient |

**WHY — ความสำคัญของแต่ละ term ใน Lid-Driven Cavity:**

- **Convection** สำคัญมากเมื่อ Re สูง — เป็นเหตุผลที่ทำให้เกิด secondary vortices
- **Viscous** สำคัญใกล้ผนัง — สร้าง boundary layer
- **Pressure** เป็นตัวกลางที่ทำให้ velocity field satisfy continuity

---

## Reynolds Number

### WHAT — Definition

$$Re = \frac{UL}{\nu} = \frac{\text{Inertial forces}}{\text{Viscous forces}}$$

| Parameter | Symbol | Unit | Typical Value |
|-----------|--------|------|---------------|
| Lid velocity | U | m/s | 1 |
| Cavity length | L | m | 1 |
| Kinematic viscosity | ν | m²/s | 0.01-0.1 |

### WHY — ทำไม Re สำคัญ?

Re บอกถึง "ธรรมชาติ" ของ flow:
- **Re ต่ำ:** Viscosity ชนะ → flow เดินตามแรงเสียดทาน อยู่กับที่
- **Re สูง:** Inertia ชนะ → flow มีพลวัต แยกจากผนัง เกิด vortices

### HOW — ควบคุม Re ด้วย ν ใน OpenFOAM

```cpp
// constant/transportProperties
nu [0 2 -1 0 0 0 0] 0.1;   // Re = 1×1/0.1 = 10
nu [0 2 -1 0 0 0 0] 0.01;  // Re = 1×1/0.01 = 100
nu [0 2 -1 0 0 0 0] 0.001; // Re = 1×1/0.001 = 1000
```

**ทำไมเปลี่ยน ν ไม่เปลี่ยน U?**
- รักษา U = 1 m/s ทำให้ non-dimensionalization ง่าย
- ผลลัพธ์เปรียบเทียบกับ Ghia ได้ตรงๆ
- Reference solution ใช้ U = 1, L = 1 → เราใช้ค่าเดียวกัน

---

## Flow Regimes

### WHAT — Flow Characteristics ตาม Re

| Re | Flow Type | Features | Physics |
|----|-----------|----------|---------|
| 10 | Laminar, creeping | Single vortex, centered | Viscous dominated |
| 100 | Laminar | Primary vortex off-center | Balance viscous/inertia |
| 400 | Laminar | Secondary corner vortices | Separation begins |
| 1000 | Laminar | Multiple corner vortices | Strong separation |
| >2000 | Transitional/Turbulent | Unsteady, 3D effects | Inertia dominated |

### WHY — ทำไม Re สูงขึ้น = ซับซ้อนขึ้น?

**Physical Mechanism:**
1. **Re สูง → inertia ชนะ viscosity**
2. **ของไหล "ไม่ยอม" เลี้ยวอย่างนุ่มนวล** → separation จากผนัง
3. **เกิด secondary vortices** ที่มุม เพราะ primary vortex "ดัน" ของไหลเข้าไป
4. **เกิด instabilities** เมื่อ Re สูงมาก → transition to turbulence

### HOW — การเลือก Re สำหรับ Validation

```cpp
// เริ่มต้นกับ Re = 100 (easy, well-documented)
nu [0 2 -1 0 0 0 0] 0.01;

// หลังจาก validate แล้ว ลอง Re = 400 (secondary vortices)
nu [0 2 -1 0 0 0 0] 0.0025;

// สุดท้าย Re = 1000 (challenging, fine mesh)
nu [0 2 -1 0 0 0 0] 0.001;
```

---

## Boundary Conditions

### WHAT — BC สำหรับ Closed Cavity

| Boundary | Velocity | Pressure | ทำไม |
|----------|----------|----------|------|
| Top (lid) | u=U, v=0 | ∂p/∂n=0 | ฝาเคลื่อนที่ |
| Bottom | u=0, v=0 | ∂p/∂n=0 | ผนังนิ่ง |
| Left | u=0, v=0 | ∂p/∂n=0 | ผนังนิ่ง |
| Right | u=0, v=0 | ∂p/∂n=0 | ผนังนิ่ง |

### WHY — ทำไม p ใช้ zeroGradient ทุกผนัง?

**Derivation จาก NS equation:**
- No-slip wall: $\mathbf{u} = 0$ → no flow through wall
- จาก NS equation ที่ผนัง (normal direction): $\frac{\partial p}{\partial n} ≈ 0$
- **แต่** ไม่มี fixedValue p เลย → ต้องใช้ `pRefCell` เป็น reference

**สรุป:** Closed cavity ไม่มี outlet → p ต้อง anchor ด้วย pRefCell

### HOW — OpenFOAM Implementation

```cpp
// 0/U
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    movingWall  // Lid
    {
        type            fixedValue;
        value           uniform (1 0 0);
    }
    
    fixedWalls  // Other walls
    {
        type            noSlip;
    }
    
    frontAndBack  // 2D assumption
    {
        type            empty;
    }
}

// 0/p
dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    movingWall
    {
        type            zeroGradient;
    }
    
    fixedWalls
    {
        type            zeroGradient;
    }
    
    frontAndBack
    {
        type            empty;
    }
}
```

**Cross-reference:** ดูรายละเอียดเพิ่มเติมเกี่ยวกับ BC ได้ที่ [Module 3: Boundary Conditions](../../03_BOUNDARY_CONDITIONS/00_Overview.md)

---

## Flow Features

### Primary Vortex

**WHAT:** โกลึ่นกลางของการหมุนวนหลักใน cavity

**Characteristics:**
- ศูนย์กลางอยู่ที่ประมาณ (0.5, 0.4-0.7) ขึ้นกับ Re
- หมุน **ตามเข็มนาฬิกา** (lid ดึงของไหลไปขวา)
- ความเข้ม (circulation) เพิ่มขึ้นตาม Re

**WHY — ทำไมหมุนตามเข็มนาฬิกา:**
1. Lid เคลื่อนที่ไปทางขวา → ดึง fluid ไปด้วย
2. Fluid ไปชนผนังขวา → ถูกบังคับไหลลง
3. ไหลลงไปชนพื้น → ถูกบังคับไหลซ้าย
4. ไหลซ้ายไปชนผนังซ้าย → ถูกบังคับไหลขึ้น
5. กลับมาที่ lid → วนซ้ำ

---

### Secondary Vortices (Re > 400)

**WHAT:** โกลึ่นกลางการหมุนวนเล็กๆ ที่เกิดที่มุม

**Characteristics:**
- เกิดที่ **มุมล่างขวาและล่างซ้าย**
- หมุน **ทวนเวลา** (opposite to primary)
- ขนาดเล็กกว่า primary มาก

**WHY — ทำไมเกิด secondary vortices?**
- Primary vortex "ดัน" ของไหลเข้ามุม
- ของไหลไม่มีที่ไป → หมุนวนในมุม
- การหมุนทวนเวลาเพราะ primary ลากไปในทิศทางตรงข้าม

---

### Corner Singularities

**WHAT — ปัญหาทางคณิตศาสตร์:** Top corners มี **velocity discontinuity**

**Details:**
- Lid (top): u = U (เคลื่อนที่)
- Wall (side): u = 0 (นิ่ง)
- **ที่จุดมุม:** ทั้งสอง BC ขัดแย้งกัน!

**WHY — ผลกระทบ:**
- Mathematically: singular point (velocity ไม่ unique)
- Numerically: อาจมี artifacts ถ้า mesh หยาบ
- Gradient สูงมาก → ต้อง mesh refinement

**HOW — แก้ไข:**
- Mesh refinement ที่มุม
- หรือใช้ smoothed BC (transition zone)
- ใน practice: mesh ละเอียดพอ → error ยอมรับได้

---

## Vortex Center Position (Reference: Ghia et al., 1982)

### WHAT — Validation Data

| Re | x/L | y/L |
|----|-----|-----|
| 100 | 0.6172 | 0.7344 |
| 400 | 0.5547 | 0.6055 |
| 1000 | 0.5313 | 0.5625 |

### WHY — ทำไว้เพื่ออะไร?

Vortex center position เป็น **global measure** ของ flow:
- Sensitive ต่อ mesh quality
- Sensitive ต่อ numerical settings
- เปรียบเทียบง่าย (single point data)

### HOW — การใช้งานตรวจสอบ simulation

**Step 1:** Extract velocity field ที่ converged state
```bash
# ใช้ paraView หรือ sample utility
postProcess -func "centerOfMass"
```

**Step 2:** หา vortex center จากผลลัพธ์
- Plot u-velocity contour
- หาจุดที่ u = v = 0 และ circulation สูงสุด

**Step 3:** เปรียบเทียบกับ Ghia
- ถ้า error < 1% → mesh/settings ถูกต้อง
- ถ้า error > 5% → refine mesh หรือ check settings

---

## PISO Algorithm

### WHAT — Pressure Implicit with Splitting of Operators

Algorithm สำหรับ transient incompressible flow ที่แก้ pressure-velocity coupling

### WHY — ทำไมใช้ PISO?

> **ปัญหา transient → ต้องการ accuracy ทุก time step**
> - PISO แก้ p หลายครั้งต่อ time step → U และ p consistent
> - เหมาะกับ unsteady flow เช่น lid-driven cavity startup

**สรุปเปรียบเทียบ:**
- **SIMPLE:** Steady-state, ช้ากว่า แต่ stable
- **PISO:** Transient, เร็ว, accurate ต่อ time step
- **PIMPLE:** Hybrid สำหรับ cases ที่ต้องการทั้งสอง

### HOW — Algorithm Steps

```
1. Predict U* (momentum without correct p)
   → Solve momentum equation ด้วย pressure จาก time step ก่อน
   
2. Solve pressure Poisson equation for p'
   → แก้สมการ Laplacian(p') = divergence(U*)
   
3. Correct U = U* - ∇p'/A
   → ปรับ velocity ให้ satisfy continuity
   
4. Repeat 2-3 for nCorrectors times
   → แก้ซ้ำจน converged ภายใน time step
   
5. Advance to next time step
   → เวลาเดินหน้า ทำซ้ำอีกครั้ง
```

### OpenFOAM Implementation

```cpp
// system/fvSolution
PISO
{
    nCorrectors     2;          // จำนวน pressure corrections
    nNonOrthogonalCorrectors 0;  // สำหรับ mesh ที่ไม่ orthogonal
    pRefCell        0;          // Cell ที่ fix reference p
    pRefValue       0;          // ค่า reference p
}
```

**ทำไม pRefCell/pRefValue สำคัญ?**
- No fixedValue p BC → p ไม่มี anchor (ไม่มีค่าสัมบูรณ์)
- ต้องกำนด reference point → pressure unique (เปลี่ยนทุกจุดเท่ากัน → ไม่เปลี่ยน flow)
- **Practical tip:** เลือก cell ไหนก็ได้ แต่สะดวกที่สุดคือ cell 0 (มุมบนซ้าย)

---

## Mesh Considerations

### WHAT — Minimum Requirements

| Re | Grid (NxN) | Notes |
|----|------------|-------|
| 10 | 10×10 | Coarse OK (viscous dominated) |
| 100 | 20×20 | Standard validation |
| 1000 | 50×50+ | Need refinement near walls |

### WHY — ทำไม Re สูงต้อง mesh ละเอียดกว่า?

**Physical Reason:**
- Re สูง → boundary layer บางลง (δ ∝ 1/√Re)
- ต้อง resolve thin layers ใกล้ผนัง
- ถ้า mesh หยาบเกิน → gradient ไม่ถูก capture → error ใน vortex position

**Numerical Reason:**
- Convection dominant → Peclet number สูง → numerical instability
- ต้อง cell size เล็ก → Peclet number < 2 (stability criterion)

---

### Grading (Near-Wall Refinement)

#### WHAT — Grading คืออะไร?

Grading คือการใช้ cell size ที่ไม่สม่ำเสมอ — เล็กที่ผนัง ใหญ่ตรงกลาง

#### WHY — ทำใช้ Grading?

**Purpose:**
1. **Efficiency:** Refine ที่ต้องการ หยาบที่ไม่สำคัญ → ประหยัด cells
2. **Accuracy:** Resolve boundary layers ที่ผนัง
3. **Stability:** Gradient สูง → ต้อง cell เล็ก

#### HOW — Grading Syntax ใน blockMesh

```cpp
// Near-wall refinement example
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

**รูปแบบ grading syntax (IMPORTANT — อย่าแก้!):**

```
((fraction_start fraction_end expansion_ratio))
```

**แต่ละพารามิเตอร์:**
- `fraction_start`: สัดส่วน block ที่ start (0-1) — ส่วนที่เป็น "ต้น"
- `fraction_end`: สัดส่วน block ที่ end (0-1) — ส่วนที่เป็น "ปลาย"
- `expansion_ratio`: อัตราขยาย cell size 
  - >1 = ใหญ่ขึ้น (cells expand)
  - <1 = เล็กลง (cells contract)

**ตัวอย่างเฉพาะ:** `((0.2 0.8 3))`
- 20% แรกของ block: cell เล็ก
- 80% หลังของ block: cell ใหญ่ 3 เท่า
- ใช้ refine ใกล้ผนัง (start)

**Multiple blocks syntax:** `((0.5 0.5 2)(0.5 0.5 0.5))`
- Block ที่ 1: ครึ่งแรกของ edge, cells expand 2x
- Block ที่ 2: ครึ่งหลังของ edge, cells uniform
- รวม: เล็กตรงกลาง → ใหญ่ตรงขอบ

---

## Mesh Independence Study

### WHAT — Definition

Mesh independence หมายถึง "ผลลัพธ์ไม่ขึ้นกับ mesh" — refine เพิ่มอีก ผลไม่เปลี่ยน

### WHY — ทำไมสำคัญ?

- ถ้า refine แล้วผลเปลี่ยน = mesh หยาบเกินไป → not converged
- ผลลัพธ์ต้อง "ไม่ขึ้นกับ mesh" → ถึงจะเชื่อถือได้
- Validation กับ reference solution ต้องใช้ mesh independent result

### HOW — วิธีทำ

**Step 1:** เลือก metric ที่ sensitive
- Vortex center position (x, y coordinates)
- Velocity magnitude ตาม centerline
- Wall shear stress

**Step 2:** รัน multiple meshes
```bash
# Coarse
blockDict -> 20×20
runSolver -> vortex_center = (0.62, 0.73)

# Medium
blockDict -> 40×40
runSolver -> vortex_center = (0.618, 0.735)

# Fine
blockDict -> 80×80
runSolver -> vortex_center = (0.6175, 0.7345)
```

**Step 3:** ตรวจสอบ convergence
- ถ้าต่างกัน < 1% ระหว่าง medium-fine = mesh independent
- ถ้าต่างกัน > 5% = refine เพิ่ม

---

## Key Takeaways

### Benchmark Significance
- Lid-Driven Cavity เป็น **benchmark problem มาตรฐาน** สำหรับ CFD validation
- มี reference solution จาก Ghia et al. (1982) ที่เชื่อถือได้และถูก cite >10,000 ครั้ง
- Geometry เรียบง่าย แต่มี physics ที่ซับซ้อนพอที่จะทดสอบ solver

### Physics Features
- **Primary vortex:** หมุนตามเข็มนาฬิกา เกิดจาก lid ดึงของไหลไปทางขวา
- **Secondary vortices:** เกิดเมื่อ Re > 400 ที่มุมล่าง หมุนทวนเวลา
- **Corner singularities:** มี velocity discontinuity ที่มุมบน ต้อง mesh refinement

### Reynolds Number Effects
- **Re ต่ำ (10):** Viscous dominated, single vortex ตรงกลาง
- **Re กลาง (100-400):** Balance viscous/inertia, primary vortex off-center
- **Re สูง (1000):** Inertia dominated, multiple secondary vortices

### Mesh Requirements
- **Re 10:** 10×10 ก็เพียงพอ
- **Re 100:** 20×20 เป็นมาตรฐาน
- **Re 1000:** 50×50+ พร้อม grading refinement ใกล้ผนัง
- **Grading syntax:** `((fraction_start fraction_end expansion_ratio))` — เล็กตรงกลาง, ใหญ่ตรงขอบ

### Boundary Conditions
- **Velocity:** Lid = fixedValue (1 0 0), Walls = noSlip
- **Pressure:** All walls = zeroGradient (ต้องมี pRefCell)
- **ทำไม p เป็น zeroGradient:** No-penetration → ∂p/∂n = 0

### Validation Approach
- เปรียบเทียบ vortex center position กับ Ghia
- Mesh independence study ด้วย 20×20, 40×40, 80×80
- Error < 1% = mesh independent

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
<summary><b>3. ทำมา corner มี velocity discontinuity?</b></summary>

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

<details>
<summary><b>5. อธิบาย grading syntax: ((0.5 0.5 2)(0.5 0.5 0.5))</b></summary>

**แตกละเอียด:**
- `((0.5 0.5 2)`: Block ที่ 1 — ครึ่งแรกของ edge, cells expand 2x
- `(0.5 0.5 0.5))`: Block ที่ 2 — ครึ่งหลังของ edge, cells uniform

**ผลลัพธ์:**
- เล็กตรงกลาง → ใหญ่ตรงขอบ
- ใช้สำหรับ refine ตรงกลาง domain
- ถ้าอยาก refine ใกล้ผนัง: เปลี่ยนเป็น `((0.2 0.8 0.5)(0.2 0.8 2))`
</details>

---

## เอกสารที่เกี่ยวข้อง

### Within This Module
- **บทก่อนหน้า:** [02_The_Workflow.md](02_The_Workflow.md) — Workflow การทำ CFD simulation
- **บทถัดไป:** [04_Step-by-Step_Tutorial.md](04_Step-by-Step_Tutorial.md) — Tutorial ละเอียดทีละ step
- **Cross-reference:** [00_Overview.md](00_Overview.md) — ภาพรวมของ Module นี้

### Related Modules
- **Boundary Conditions:** [Module 3: Boundary Conditions](../../03_BOUNDARY_CONDITIONS/00_Overview.md) — รายละเอียดเพิ่มเติมเกี่ยวกับ BC types
- **Numerical Methods:** [Module 2: Finite Volume Method](../../02_FINITE_VOLUME_METHOD/00_Overview.md) — วิธี discretization

### Reference Papers
- **Ghia, U., Ghia, K. N., & Shin, C. T. (1982).** High-Re solutions for incompressible flow using the Navier-Stokes equations and a multigrid method. *Journal of Computational Physics*, 48(3), 387-411.
  - **DOI:** [10.1016/0021-9991(82)90058-4](https://doi.org/10.1016/0021-9991(82)90058-4)
  - **ทำมา:** Provides benchmark data สำหรับ Re = 100, 400, 1000
  - **Grid:** 129×129 สำหรับ Re = 1000 (very fine!)
  - **Method:** Multigrid with second-order accurate discretization