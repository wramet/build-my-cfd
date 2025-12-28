# ภาพรวม: Lid-Driven Cavity Simulation

การจำลอง CFD แรกของคุณใน OpenFOAM ด้วย Benchmark Problem คลาสสิก

---

## ทำไมต้อง Lid-Driven Cavity?

- **Benchmark มาตรฐาน** — มีข้อมูลเปรียบเทียบ (Ghia et al., 1982)
- **Geometry เรียบง่าย** — แค่กล่องสี่เหลี่ยม
- **Physics สมบูรณ์** — Vortex, shear layer, boundary layer
- **เรียนรู้ workflow ครบ** — Pre-process → Solve → Post-process

---

## ปัญหา

กล่องสี่เหลี่ยมบรรจุของไหล ฝาบนเคลื่อนที่ → สร้าง recirculating vortex

| Parameter | Value |
|-----------|-------|
| Domain | 1×1×0.1 m (quasi-2D) |
| Lid velocity | 1 m/s (+x) |
| Other walls | Stationary (no-slip) |
| Fluid | Incompressible, Newtonian |
| Re | 10-1000 |

---

## สมการควบคุม

**Continuity:**
$$\nabla \cdot \mathbf{u} = 0$$

**Momentum:**
$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu\nabla^2\mathbf{u}$$

**Reynolds Number:**
$$Re = \frac{UL}{\nu}$$

---

## OpenFOAM Case Structure

```
cavity/
├── 0/
│   ├── U           # Velocity field
│   └── p           # Pressure field
├── constant/
│   ├── polyMesh/   # Mesh (from blockMesh)
│   └── transportProperties  # ν
└── system/
    ├── blockMeshDict   # Mesh definition
    ├── controlDict     # Time control
    ├── fvSchemes       # Discretization
    └── fvSolution      # Solver settings
```

---

## Boundary Conditions

### Velocity (0/U)

```cpp
boundaryField
{
    movingWall  { type fixedValue; value uniform (1 0 0); }
    fixedWalls  { type noSlip; }
    frontAndBack { type empty; }
}
```

### Pressure (0/p)

```cpp
boundaryField
{
    movingWall   { type zeroGradient; }
    fixedWalls   { type zeroGradient; }
    frontAndBack { type empty; }
}
```

---

## Solver: icoFoam

- **Type:** Incompressible, laminar, transient
- **Algorithm:** PISO (Pressure Implicit with Splitting of Operators)
- **Use case:** Low-Re laminar flows

---

## Workflow

```bash
# 1. สร้าง mesh
blockMesh

# 2. ตรวจสอบ mesh
checkMesh

# 3. รัน solver
icoFoam

# 4. ดูผลลัพธ์
paraFoam
```

---

## ผลลัพธ์ที่คาดหวัง

| Feature | Re = 10 | Re = 100 |
|---------|---------|----------|
| Primary vortex center | (0.50, 0.40) | (0.62, 0.74) |
| Secondary vortices | ไม่มี | มุมล่าง |
| Max velocity | 1 m/s (lid) | 1 m/s (lid) |

---

## โครงสร้างบทเรียน

| ไฟล์ | เนื้อหา |
|------|---------| 
| [01_Introduction.md](01_Introduction.md) | บทนำ CFD workflow |
| [02_The_Workflow.md](02_The_Workflow.md) | Pre/Solve/Post-processing |
| [03_The_Lid-Driven_Cavity_Problem.md](03_The_Lid-Driven_Cavity_Problem.md) | ฟิสิกส์และ math |
| [04_Step-by-Step_Tutorial.md](04_Step-by-Step_Tutorial.md) | Hands-on tutorial |
| [05_Expected_Results.md](05_Expected_Results.md) | Validation |
| [06_Exercises.md](06_Exercises.md) | แบบฝึกหัด |

---

## Concept Check

<details>
<summary><b>1. ทำไม pressure ใช้ zeroGradient ที่ทุกผนัง?</b></summary>

เพราะไม่มี flow ผ่านผนัง (no-slip) ดังนั้น $\frac{\partial p}{\partial n} = 0$ และ reference pressure ถูกกำหนดผ่าน `pRefCell/pRefValue` ใน fvSolution
</details>

<details>
<summary><b>2. empty BC คืออะไร?</b></summary>

BC สำหรับ 2D simulation ใน OpenFOAM — บอกว่าไม่มี variation ในทิศทางนั้น (z-direction ใน cavity case)
</details>

<details>
<summary><b>3. icoFoam ใช้ได้กับ turbulent flow ไหม?</b></summary>

ไม่ได้ — icoFoam สำหรับ laminar เท่านั้น สำหรับ turbulent ใช้ `pimpleFoam` + turbulence model
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [../03_BOUNDARY_CONDITIONS/00_Overview.md](../03_BOUNDARY_CONDITIONS/00_Overview.md) — Boundary Conditions
- **บทถัดไป:** [01_Introduction.md](01_Introduction.md) — บทนำ