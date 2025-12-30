# ภาพรวม: Lid-Driven Cavity Simulation

การจำลอง CFD แรกของคุณใน OpenFOAM ด้วย Benchmark Problem คลาสสิก

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- **อธิบาย** ว่าทำไม Lid-Driven Cavity จึงเป็น benchmark มาตรฐานสำหรับ CFD validation
- **เข้าใจ** โครงสร้าง directory และไฟล์พื้นฐานของ OpenFOAM case
- **ระบุ** boundary conditions ที่เหมาะสมสำหรับปัญหา quasi-2D
- **แยกแยะ** บทบาทของแต่ละไฟล์ใน OpenFOAM case structure (0/, constant/, system/)
- **เปรียบเทียบ** ผลลัพธ์กับ reference data สำหรับ validation

---

## ภาพรวมบทเรียน

> **🎯 3W FRAMEWORK**
> 
> **WHAT (อะไร):** Lid-Driven Cavity Benchmark — ปัญหาการไหลของของไหลในกล่องสี่เหลี่ยมที่ฝาบนเคลื่อนที่ ซึ่งสร้าง recirculating vortex ภายในโดเมน
> 
> **WHY (ทำไม):** เป็นปัญหา benchmark มาตรฐา�ใน CFD ที่มี reference data ที่เชื่อถือได้ (Ghia et al., 1982) ใช้สำหรับ validation solver และเรียนรู้ workflow การจำลองแบบครบวงจร (Pre-process → Solve → Post-process) ด้วย geometry ที่เรียบง่าย แต่ physics ที่ซับซ้อนพอสมควร
> 
> **HOW (อย่างไร):** ผ่านขั้นตอน OpenFOAM workflow ทั้งหมด ตั้งแต่การสร้าง mesh ด้วย `blockMesh`, การตั้งค่า boundary conditions, การรัน transient solver `icoFoam`, การดูผลลัพธ์ด้วย `paraFoam`, และการ validate กับ reference data

---

## ปัญหา Lid-Driven Cavity

> **🎯 3W FRAMEWORK**
> 
> **WHAT (อะไร):** ปัญหาการไหลของของไหลในกล่องสี่เหลี่ยมจัตุรัสที่ฝาบน (lid) เคลื่อนที่ด้วยความเร็วคงที่ ส่งผลให้เกิดการหมุนวนของของไหล (recirculating vortex) ภายในโดเมน
> 
> **WHY (ทำไม):** เป็นปัญหาที่เหมาะสำหรับการเรียนรู้ CFD workflow เพราะมี geometry เรียบง่าย แต่ยังคง physics ที่น่าสนใจ เช่น vortex formation, shear layers, และ boundary layers อีกทั้งยังมีข้อมูล reference ที่ดีสำหรับ validation
> 
> **HOW (อย่างไร):** แก้สมการ Navier-Stokes สำหรับของไหลไร้การบีบอัด (incompressible) แบบ laminar ในรูปแบบ transient ด้วยเงื่อนไขขอบเขต no-slip ที่ผนังทั้งหมด และ lid ที่เคลื่อนที่

### รายละเอียดปัญหา

**Physical Setup:**
- กล่องสี่เหลี่ยมบรรจุของไหล
- ฝาบนเคลื่อนที่ด้วยความเร็วคงที่ → สร้าง recirculating vortex
- ผนังอื่นๆ อยู่นิ่ง (stationary)

**Parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| Domain | 1×1×0.1 m | Quasi-2D: mesh 1 cell ในทิศ z |
| Lid velocity | 1 m/s (+x direction) | Upper wall velocity |
| Other walls | 0 m/s | Stationary (no-slip) |
| Fluid | Incompressible, Newtonian | Constant properties |
| Reynolds Number | 10-1000 | Re = UL/ν |

> **💡 ทำไมเรียก Quasi-2D?**
> 
> **WHAT (อะไร):** Mesh ที่มีเพียง 1 cell ในทิศทาง z (depth = 0.1 m) แต่ยังคงเป็น 3D mesh จริง
> 
> **WHY (ทำไม):** OpenFOAM ทำงานกับ 3D mesh เท่านั้น ดังนั้นเพื่อจำลองปัญหา 2D เราจึง extrude 2D geometry ด้วย thickness เล็กน้อย และใช้ boundary condition พิเศษเพื่อกำจัด variation ในทิศทาง z
> 
> **HOW (อย่างไร):** ใช้ `empty` BC ที่ frontAndBack planes → ไม่มี flux ผ่านผนัง z และไม่มีการแก้สมการในทิศทางนั้น → Physics จึงเป็น 2D แม้ว่า mesh จะเป็น 3D extruded

---

## สมการควบคุม

> **🎯 3W FRAMEWORK**
> 
> **WHAT (อะไร):** สมการ Navier-Stokes สำหรับของไหลไร้การบีบอัด (incompressible) แบบ laminar ซึ่งประกอบด้วยสมการความต่อเนื่อง (continuity) และสมการโมเมนตัม (momentum)
> 
> **WHY (ทำไม):** เป็นรากฐานคณิตศาสตร์ที่อธิบายการเคลื่อนที่ของของไหล Newtonian ที่เราจะแก้ด้วย numerical method ใน OpenFOAM
> 
> **HOW (อย่างไร):** icoFoam solver ใช้ Finite Volume Method (FVM) เพื่อ discretize สมการเหล่านี้และแก้ด้วย PISO algorithm สำหรับ pressure-velocity coupling

### Continuity Equation (สมการความต่อเนื่อง)

$$\nabla \cdot \mathbf{u} = 0$$

- **Physical meaning:** ปริมาตรของไหลเข้า = ปริมาตรของไหลออก (conservation of mass)
- **สำหรับ incompressible flow:** ความหนาแน่นคงที่ → divergence ของ velocity เป็นศูนย์

### Momentum Equation (สมการโมเมนตัม)

$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu\nabla^2\mathbf{u}$$

| Term | Description | Physical Meaning |
|------|-------------|------------------|
| $\frac{\partial \mathbf{u}}{\partial t}$ | Unsteady term | การเปลี่ยนแปลงความเร็วตามเวลา |
| $(\mathbf{u} \cdot \nabla)\mathbf{u}$ | Convection term | การพาของโมเมนตัมโดย velocity field เอง |
| $-\frac{1}{\rho}\nabla p$ | Pressure gradient | แรงที่เกิดจากความต่างความดัน |
| $\nu\nabla^2\mathbf{u}$ | Diffusion term | ความหนืด/viscous forces |

### Reynolds Number

$$Re = \frac{UL}{\nu} = \frac{(1\text{ m/s})(1\text{ m})}{\nu}$$

| Re | Flow Characteristics |
|----|---------------------|
| 10 | Laminar, symmetric vortex |
| 100 | Laminar, vortex shifts toward lid |
| 400 | Laminar, corner vortices appear |
| 1000 | Transition to turbulence (ความแม่นยำลดลง) |

---

## OpenFOAM Case Structure

> **🎯 3W FRAMEWORK**
> 
> **WHAT (อะไร):** โครงสร้าบ directory มาตรฐานของ OpenFOAM case ซึ่งแบ่งเป็น 3 ส่วนหลัก: 0/, constant/, และ system/
> 
> **WHY (ทำไม):** OpenFOAM ต้องการการจัดระเบียบไฟล์แบบเฉพาะเพื่อให้ solver สามารถค้นหาและอ่านข้อมูลได้อัตโนมัติ แต่ละ directory มีบทบาทเฉพาะที่ชัดเจน
> 
> **HOW (อย่างไร):** สร้าง directory structure ตามรูปแบบมาตรฐาน วางไฟล์ที่เหมาะสมในแต่ละ directory และ OpenFOAM solver จะจัดการข้อมูลอัตโนมัติ

### Directory Structure

```
cavity/
├── 0/                          # 📁 Initial & Boundary Conditions
│   ├── U                       # Velocity field (initial + BC)
│   └── p                       # Pressure field (initial + BC)
│
├── constant/                   # 📁 Time-independent Data
│   ├── polyMesh/               # Mesh (generated by blockMesh)
│   │   └── blockMeshDict       # Mesh definition (→ generates mesh files)
│   └── transportProperties     # Fluid properties (ν = kinematic viscosity)
│
└── system/                     # 📁 Simulation Control
    ├── blockMeshDict           # Mesh generation parameters
    ├── controlDict             # Time control (start/end, write interval)
    ├── fvSchemes               # Discretization schemes (div, grad, laplacian)
    └── fvSolution              # Linear solver settings & algorithm (PISO)
```

### คำอธิบายแต่ละส่วน

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| **0/** | เก็บ fields ที่ต้องการ initial และ boundary conditions | U (velocity), p (pressure) |
| **constant/** | ข้อมูลที่ไม่เปลี่ยนตามเวลา | polyMesh/, transportProperties |
| **system/** | ควบคุมการแก้สมการ (numerical settings) | controlDict, fvSchemes, fvSolution |

> **📖 ดูเพิ่มเติม:** รายละเอียดการตั้งค่าแต่ละไฟล์อยู่ใน [02_The_Workflow.md](02_The_Workflow.md)

---

## Boundary Conditions

> **🎯 3W FRAMEWORK**
> 
> **WHAT (อะไร):** เงื่อนไขขอบเขต (boundary conditions) คือการระบุค่าของ variables ที่ผนังของโดเมน ซึ่งมีผลต่อการแก้สมการ Navier-Stokes
> 
> **WHY (ทำไม):** BC ที่ถูกต้องจำเป็นอย่างยิ่งสำหรับ well-posed problem และมีผลต่อความแม่นยำของผลลัพธ์
> 
> **HOW (อย่างไร):** ระบุ BC ในไฟล์ 0/U และ 0/p โดยแต่ละ patch ต้องมี type และ value ที่เหมาะสมกับ physics

### Velocity BC (0/U)

```cpp
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    movingWall  
    { 
        type            fixedValue;     // ⬅ Fixed velocity
        value           uniform (1 0 0); // 1 m/s in +x direction
    }
    
    fixedWalls  
    { 
        type            noSlip;         // ⬅ u = 0 (automatically)
    }
    
    frontAndBack 
    { 
        type            empty;          // ⬅ 2D BC (no variation in z)
    }
}
```

**BC Types Explained:**

| Type | Meaning | Use Case |
|------|---------|----------|
| `fixedValue` | กำหนดค่าคงที่ | Moving wall ที่ lid |
| `noSlip` | Velocity = 0 ที่ผนัง | Stationary walls |
| `empty` | ไม่มีการแก้สมการ | Quasi-2D (front/back) |

> **💡 ทำไม `noSlip` ไม่ต้องระบุ value?**
> เพราะ `noSlip` คือ shorthand สำหรับ `fixedValue` ที่มี value = uniform (0 0 0) → velocity เป็นศูนย์ที่ผนัง

### Pressure BC (0/p)

```cpp
dimensions      [0 2 -2 0 0 0 0];      // Pressure: [kg/(m·s²)]

internalField   uniform 0;

boundaryField
{
    movingWall   
    { 
        type            zeroGradient;   // ⬅ ∂p/∂n = 0
    }
    
    fixedWalls   
    { 
        type            zeroGradient;   // ⬅ ∂p/∂n = 0
    }
    
    frontAndBack 
    { 
        type            empty;          // ⬅ 2D BC
    }
}
```

> **🤔 ทำไม Pressure ใช้ `zeroGradient` ที่ทุกผนัง?**
> 
> เพราะไม่มี flow ผ่านผนัง (no-slip condition) ดังนั้น $\frac{\partial p}{\partial n} = 0$ ที่ผนัง แต่ reference pressure ยังต้องถูกกำหนดเพื่อ prevent floating values → เราทำใน `fvSolution` ด้วย `pRefCell/pRefValue`

### BC Summary

| Boundary | Velocity (U) | Pressure (p) |
|----------|--------------|--------------|
| movingWall (lid) | `fixedValue (1 0 0)` | `zeroGradient` |
| fixedWalls (sides/bottom) | `noSlip` | `zeroGradient` |
| frontAndBack | `empty` | `empty` |

> **📖 ดูเพิ่มเติม:** รายละเอียด BC types และการเลือก BC ที่เหมาะสมใน [../03_BOUNDARY_CONDITIONS/00_Overview.md](../03_BOUNDARY_CONDITIONS/00_Overview.md)

---

## Solver: icoFoam

> **🎯 3W FRAMEWORK**
> 
> **WHAT (อะไร):** `icoFoam` เป็น transient solver สำหรับ incompressible, laminar, Newtonian flows ใน OpenFOAM
> 
> **WHY (ทำไม):** เหมาะสำหรับ Lid-Driven Cavity เพราะ problem นี้เป็น laminar flow (Re < 1000), incompressible, และต้องการ transient solution เพื่อดู evolution ของ vortex
> 
> **HOW (อย่างไร):** ใช้ PISO (Pressure Implicit with Splitting of Operators) algorithm สำหรับ pressure-velocity coupling และแก้สมการ Navier-Stokes แบบ transient

### Solver Characteristics

| Property | Value | Description |
|----------|-------|-------------|
| **Flow Type** | Incompressible | ρ = constant |
| **Regime** | Laminar | No turbulence model |
| **Time** | Transient | ∂/∂t ≠ 0 |
| **Algorithm** | PISO | Pressure-velocity coupling |
| **Geometry** | 3D (or quasi-2D) | FVM on unstructured meshes |

### PISO Algorithm Loop

```
FOR EACH TIME STEP:
  1. Predict velocity (momentum predictor)
  2. SOLVE PRESSURE (PISO loop):
     - Correct velocity with pressure gradient
     - Repeat 2-3 times for convergence
  3. Update fields (final velocity)
  4. Write results (if at write time)
```

> **💡 ทำไมต้อง PISO?**
> 
> **WHAT:** PISO = Pressure Implicit with Splitting of Operators
> 
> **WHY:** แก้ปัญหา pressure-velocity coupling ใน incompressible flows โดยไม่ต้องอิง pressure-correction จาก time step ก่อนหน้า เหมาะกับ transient simulations
> 
> **HOW:** Predictor-corrector แบบ iterative ที่ converge ใน 2-3 iterations ต่อ time step

### When to Use icoFoam?

| ✅ Use icoFoam for... | ❌ Use other solvers for... |
|----------------------|---------------------------|
| Laminar flows (Re < ~2000) | Turbulent flows → `pimpleFoam` |
| Incompressible fluids | Compressible flows → `rhoPimpleFoam` |
| Newtonian fluids | Non-Newtonian → `nonNewtonianIcoFoam` |
| Transient simulations | Steady-state → `simpleFoam` |

> **📖 ดูเพิ่มเติม:** รายละเอียดการใช้งาน solver และการตั้งค่าอยู่ใน [02_The_Workflow.md](02_The_Workflow.md)

---

## Workflow Overview

> **🎯 3W FRAMEWORK**
> 
> **WHAT (อะไร):** ขั้นตอนการจำลอง CFD ใน OpenFOAM ซึ่งประกอบด้วย 3 ขั้นตอนหลัก: Pre-processing, Solving, และ Post-processing
> 
> **WHY (ทำไม):** เพื่อให้ได้ผลลัพธ์ที่ถูกต้อง ต้องทำตามลำดับขั้นตอนอย่างเป็นระบบ โดยแต่ละขั้นตอนมีผลต่อขั้นตอนถัดไป
> 
> **HOW (อย่างไร):** รันคำสั่ง OpenFOAM ตามลำดับ ตรวจสอบผลลัพธ์ในแต่ละขั้นตอน และดูผลสุดท้ายด้วย visualization tools

### ขั้นตอนพื้นฐาน

```bash
# ========== PRE-PROCESSING ==========
# 1. สร้าง mesh
blockMesh

# 2. ตรวจสอบ mesh quality
checkMesh

# ========== SOLVING ==========
# 3. รัน solver
icoFoam

# ========== POST-PROCESSING ==========
# 4. ดูผลลัพธ์ใน ParaView
paraFoam
```

### คำอธิบายแต่ละขั้นตอน

| Step | Command | Purpose | Output |
|------|---------|---------|--------|
| **1** | `blockMesh` | สร้าง mesh จาก blockMeshDict | `constant/polyMesh/` |
| **2** | `checkMesh` | ตรวจสอบคุณภาพ mesh | Mesh quality report |
| **3** | `icoFoam` | แก้สมการ Navier-Stokes | Time directories (0.1/, 0.2/, ...) |
| **4** | `paraFoam` | เปิดผลลัพธ์ใน ParaView | Visualization |

> **📖 ดูเพิ่มเติม:** รายละเอียดเชิงลึกของแต่ละขั้นตอนอยู่ใน [02_The_Workflow.md](02_The_Workflow.md) และ tutorial แบบ step-by-step อยู่ใน [04_Step-by-Step_Tutorial.md](04_Step-by-Step_Tutorial.md)

---

## ผลลัพธ์ที่คาดหวัง

> **🎯 3W FRAMEWORK**
> 
> **WHAT (อะไร):** ผลลัพธ์ของ Lid-Driven Cavity ที่ควรได้รับจากการจำลอง ซึ่งแตกต่างตามค่า Reynolds number
> 
> **WHY (ทำไม):** การรู้ล่วงหน้าว่าควรได้ผลลัพธ์แบบไหน ช่วยในการ validate ว่าการจำลองถูกต้องหรือไม่ และช่วย detect errors ได้เร็วขึ้น
> 
> **HOW (อย่างไร):** เปรียบเทียบ vortex center position, velocity profiles, และ flow patterns กับ reference data จาก Ghia et al. (1982)

### Expected Flow Features

ตามค่า Reynolds number ที่แตกต่างกัน จะได้ลักษณะการไหลที่แตกต่างกัน:

| Feature | Re = 10 | Re = 100 | Re = 400 | Re = 1000 |
|---------|---------|----------|----------|-----------|
| **Primary vortex center** | (0.50, 0.40) | (0.62, 0.74) | (0.55, 0.60) | Shifts toward lid |
| **Secondary vortices** | ไม่มี | มุมล่างเริ่มเกิด | ชัดเจนที่มุมล่าง | มุมบน + ล่าง |
| **Vortex strength** | อ่อน | ปานกลาง | แรง | แรงมาก |
| **Max velocity** | 1 m/s (lid) | 1 m/s (lid) | 1 m/s (lid) | 1 m/s (lid) |

### Validation Metrics

**1. Vortex Center Position**
- วัดจากจุดที่ velocity = 0 หรือจาก streamlines
- เปรียบเทียบกับ Ghia et al. (1982) benchmark data

**2. Velocity Profiles**
- ตัด profile และ horizontal/vertical centerlines
- เปรียบเทียบ u-velocity และ v-velocity

**3. Convergence**
- Monitor residuals ของ pressure และ velocity
- ค่าควรลดลงอย่างน้อย 4-6 orders of magnitude

> **📖 ดูเพิ่มเติม:** รายละเอียดการ validation และ comparison กับ reference data อยู่ใน [05_Expected_Results.md](05_Expected_Results.md)

---

## โครงสร้างบทเรียน

บทนี้เป็นส่วนหนึ่งของ Module 04: First Simulation ซึ่งครอบคลุม workflow การจำลอง CFD แรกใน OpenFOAM

| ไฟล์ | เนื้อหาหลัก | 🎯 Focus |
|------|---------------|----------|
| **[00_Overview.md](00_Overview.md)** | 📍 ภาพรวมทั้งหมด | Concepts, case structure, BC overview |
| **[01_Introduction.md](01_Introduction.md)** | บทนำ CFD workflow | Workflow concepts, ความรู้พื้นฐาน |
| **[02_The_Workflow.md](02_The_Workflow.md)** | Pre/Solve/Post-processing แบบละเอียด | คำสั่ง OpenFOAM และการตั้งค่า |
| **[03_The_Lid-Driven_Cavity_Problem.md](03_The_Lid-Driven_Cavity_Problem.md)** | ฟิสิกส์และ math | สมการ, dimensionless numbers |
| **[04_Step-by-Step_Tutorial.md](04_Step-by-Step_Tutorial.md)** | Hands-on tutorial | ทำตามได้เลย แบบละเอียด |
| **[05_Expected_Results.md](05_Expected_Results.md)** | Validation | Compare กับ reference data |
| **[06_Exercises.md](06_Exercises.md)** | แบบฝึกหัด | Practice ท้ายบท |

> **💡 แนะนำการอ่าน:** เริ่มจาก 00 (overview) → 01 (concepts) → 04 (tutorial) → 02 (deep dive) → 03 (theory) → 05 (validation) → 06 (exercises)

---

## Concept Check

ทดสอบความเข้าใจของคุณด้วยคำถามเหล่านี้:

<details>
<summary><b>1. ทำไม pressure ใช้ zeroGradient ที่ทุกผนัง?</b></summary>

**WHAT:** `zeroGradient` BC หมายถึง ∂p/∂n = 0 (derivative ในทิศปกติของผนัง = 0)

**WHY:** เพราะไม่มี flow ผ่านผนัง (no-slip condition) ดังนั้น pressure gradient ในทิศที่ตั้งฉากกับผนังจึงเป็นศูนย์

**HOW:** แต่ reference pressure ยังต้องถูกกำหนดเพื่อป้องกัน floating values → เราทำใน `fvSolution` ด้วย `pRefCell/pRefValue` ซึ่งจะ set pressure = 0 ที่ cell ที่ระบุ
</details>

<details>
<summary><b>2. `empty` BC คืออะไร และทำไมต้องใช้?</b></summary>

**WHAT:** `empty` BC เป็น boundary condition พิเศษสำหรับ 2D simulation ใน OpenFOAM

**WHY:** OpenFOAM solver ทำงานกับ 3D mesh เท่านั้น ดังนั้นเพื่อจำลองปัญหา 2D เราต้อง extrude geometry และใช้ `empty` BC เพื่อ "ลบ" dimension หนึ่งออก

**HOW:** ใช้ `empty` ที่ frontAndBack planes → OpenFOAM จะไม่แก้สมการในทิศทาง z (no flux, no variation) → Physics จึงเป็น 2D แม้ว่า mesh จะเป็น 3D
</details>

<details>
<summary><b>3. `icoFoam` ใช้ได้กับ turbulent flow ไหม?</b></summary>

**WHAT:** `icoFoam` เป็น solver สำหรับ **incompressible**, **laminar**, **transient** flows

**WHY:** ชื่อ "ico" มาจาก "Incompressible COde" และไม่มี turbulence model ใน solver นี้

**HOW:**
- ✅ ใช้ `icoFoam` สำหรับ laminar flows (Re < ~2000)
- ❌ สำหรับ turbulent flows ให้ใช้ `pimpleFoam` + turbulence model (เช่น k-ε, k-ω SST)

Lid-Driven Cavity ที่ Re = 10-1000 อยู่ใน laminar regime → เหมาะกับ `icoFoam`
</details>

<details>
<summary><b>4. ทำไม Lid-Driven Cavity จึงเป็น benchmark ที่ดี?</b></summary>

**WHAT:** Benchmark คือปัญหามาตรฐานที่ใช้ทดสอบ/validate solvers

**WHY:**
- ✅ Geometry เรียบง่าย (กล่องสี่เหลี่ยม) → ง่ายต่อการ mesh
- ✅ Physics สมบูรณ์ (vortex, shear, boundary layers) → ทดสอบ solver capabilities
- ✅ มี reference data ที่เชื่อถือได้ (Ghia et al., 1982) → validate ได้
- ✅ Re number ปรับได้ → test multiple regimes

**HOW:** ใช้เปรียบเทียบ vortex center, velocity profiles, และ convergence กับ reference data
</details>

---

## 📚 Key Takeaways

สิ่งสำคัญที่ควรจำจากบทนี้:

### 🎯 Core Concepts

1. **Lid-Driven Cavity เป็น benchmark มาตรฐาน** — มี geometry เรียบง่ายแต่ physics สมบูรณ์ ใช้ validate solvers และเรียนรู้ CFD workflow

2. **OpenFOAM case structure แบ่งเป็น 3 ส่วน:**
   - `0/` — Initial และ boundary conditions (U, p)
   - `constant/` — Mesh และ fluid properties (transportProperties)
   - `system/` — Numerical settings (controlDict, fvSchemes, fvSolution)

3. **Boundary conditions ต้องเหมาะสมกับ physics:**
   - `fixedValue` — กำหนดค่าโดยตรง (moving wall)
   - `noSlip` — Velocity = 0 ที่ผนัง
   - `zeroGradient` — ∂p/∂n = 0 (pressure ที่ผนัง)
   - `empty` — สำหรับ quasi-2D

### 🔧 Practical Skills

4. **Workflow พื้นฐาน:** `blockMesh` → `checkMesh` → `icoFoam` → `paraFoam`

5. **`icoFoam` สำหรับ laminar, incompressible, transient flows** — ใช้ PISO algorithm สำหรับ pressure-velocity coupling

6. **Validation สำคัญ** — เปรียบเทียบผลลัพธ์ (vortex center, velocity profiles) กับ reference data เพื่อยืนยันความถูกต้อง

### 🔍 Theory Connection

7. **สมการ Navier-Stokes** ถูก discretize ด้วย FVM และแก้ด้วย PISO algorithm เพื่อหา velocity และ pressure fields

8. **Reynolds number ควบคุม flow characteristics** — ยิ่ง Re สูง ยิ่งมี secondary vortices และ complexity เพิ่มขึ้น

---

## 📖 เอกสารที่เกี่ยวข้อง

### บทก่อนหน้า

- **[Module 03: Boundary Conditions](../03_BOUNDARY_CONDITIONS/00_Overview.md)** — เรียนรู้เกี่ยวกับ boundary conditions ใน OpenFOAM อย่างละเอียด
  - ประเภทของ BC (Dirichlet, Neumann, Robin)
  - การเลือก BC ที่เหมาะสม
  - BC ที่พบบ่อยใน OpenFOAM

### บทถัดไปใน Module นี้

- **[01_Introduction.md](01_Introduction.md)** — บทนำสู่ CFD workflow และแนวคิดพื้นฐาน
- **[02_The_Workflow.md](02_The_Workflow.md)** — รายละเอียดเชิงลึกของแต่ละขั้นตอน (Pre/Solve/Post)
- **[04_Step-by-Step_Tutorial.md](04_Step-by-Step_Tutorial.md)** — Tutorial แบบ hands-on ทำตามได้เลย

### อ้างอิง

- **Ghia et al. (1982)** — "High-Re solutions for incompressible flow using the Navier-Stokes equations and a multigrid method" — **Journal of Computational Physics** 48(3): 387-411
  - Reference data สำหรับ Lid-Driven Cavity benchmark

---

**📍 คุณอยู่ที่: Module 04 → First Simulation → Overview**

**ขั้นตอนถัดไป:** อ่าน [01_Introduction.md](01_Introduction.md) เพื่อเรียนรู้ CFD workflow อย่างละเอียด