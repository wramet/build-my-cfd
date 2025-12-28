# แนวคิดพื้นฐาน FVM

Finite Volume Method แบ่งโดเมนเป็น **Control Volumes (Cells)** และใช้หลักการอนุรักษ์กับแต่ละ Cell

---

## หลักการ Control Volume

### Flux Balance

สำหรับแต่ละ Cell:

$$\frac{d}{dt}\int_V \phi\, dV + \sum_f \mathbf{F}_f \cdot \mathbf{S}_f = \int_V S\, dV$$

**ความหมาย:**
- การเปลี่ยนแปลงในเวลา + Flux ผ่าน Faces = Sources

**คุณสมบัติสำคัญ:**
- Flux ที่ออกจาก Cell A = Flux ที่เข้า Cell B → **Conservation**
- ค่าตัวแปรเก็บที่ **Cell Centers**
- Flux คำนวณที่ **Face Centers**

### Cell-Centered Storage

```
Cell P ─── Face f ─── Cell N
  │           │           │
 φ_P         φ_f         φ_N
(stored)  (interpolate) (stored)
```

**ข้อมูลเรขาคณิต:**

| ตัวแปร | ความหมาย | OpenFOAM |
|--------|---------|---------|
| $V_P$ | Cell Volume | `mesh.V()` |
| $\mathbf{S}_f$ | Face Area Vector | `mesh.Sf()` |
| $\mathbf{d}_{PN}$ | Distance P→N | `mesh.delta()` |

---

## สมการอนุรักษ์

### 1. Mass (Continuity)

$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$$

**Incompressible:** $\nabla \cdot \mathbf{u} = 0$

**OpenFOAM:** บังคับผ่าน pressure correction (SIMPLE/PISO)

### 2. Momentum (Navier-Stokes)

$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

| พจน์ | ความหมาย | OpenFOAM |
|------|---------|---------|
| $\rho \partial\mathbf{u}/\partial t$ | Local acceleration | `fvm::ddt(rho, U)` |
| $\rho (\mathbf{u} \cdot \nabla) \mathbf{u}$ | Convection | `fvm::div(phi, U)` |
| $-\nabla p$ | Pressure force | `fvc::grad(p)` |
| $\mu \nabla^2 \mathbf{u}$ | Viscous force | `fvm::laplacian(mu, U)` |

### 3. Energy

$$\rho c_p \frac{\partial T}{\partial t} + \rho c_p \mathbf{u} \cdot \nabla T = k \nabla^2 T + Q$$

**OpenFOAM Files:**
- `0/T` หรือ `0/h` (enthalpy)
- `constant/thermophysicalProperties`

---

## Pressure-Velocity Coupling

สำหรับ Incompressible flow ความดันไม่ได้มาจาก EOS แต่บังคับให้ $\nabla \cdot \mathbf{u} = 0$

| Algorithm | ใช้เมื่อ | OpenFOAM Solver |
|-----------|---------|-----------------|
| **SIMPLE** | Steady-state | `simpleFoam` |
| **PISO** | Transient, Δt เล็ก | `pisoFoam` |
| **PIMPLE** | Transient, Δt ใหญ่ | `pimpleFoam` |

**การตั้งค่าใน `system/fvSolution`:**

```cpp
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    residualControl { p 1e-4; U 1e-4; }
}

// หรือ
PIMPLE
{
    nOuterCorrectors 2;
    nCorrectors 1;
}
```

---

## General Transport Equation

ทุกสมการอนุลักษณ์เขียนได้ในรูป:

$$\underbrace{\frac{\partial \phi}{\partial t}}_{\text{Transient}} + \underbrace{\nabla \cdot (\mathbf{u}\phi)}_{\text{Convection}} = \underbrace{\nabla \cdot (D \nabla \phi)}_{\text{Diffusion}} + \underbrace{S}_{\text{Source}}$$

**OpenFOAM Implementation:**

```cpp
fvScalarMatrix phiEqn
(
    fvm::ddt(phi)              // Transient
  + fvm::div(phi, U)           // Convection
  - fvm::laplacian(D, phi)     // Diffusion
 ==
    Su                         // Source
);
phiEqn.solve();
```

---

## Files ที่เกี่ยวข้อง

| Location | เนื้อหา |
|----------|---------|
| `constant/polyMesh/` | Mesh topology (cells, faces, points) |
| `constant/transportProperties` | ν, ρ, μ |
| `constant/turbulenceProperties` | Turbulence model |
| `0/` | Initial & Boundary Conditions |
| `system/fvSchemes` | Discretization Schemes |
| `system/fvSolution` | Linear Solvers, Algorithms |

---

## Concept Check

<details>
<summary><b>1. ทำไม FVM ถึง "อนุรักษ์" โดยธรรมชาติ?</b></summary>

เพราะ Flux ที่ Face คำนวณครั้งเดียวและใช้ร่วมกันระหว่าง 2 Cells → สิ่งที่ออกจาก Cell A จะเข้า Cell B พอดี ไม่มีการสร้างหรือทำลาย
</details>

<details>
<summary><b>2. ในสมการโมเมนตัม ทำไม pressure gradient ใช้ fvc ไม่ใช่ fvm?</b></summary>

เพราะ $-\nabla p$ ไม่มี $\mathbf{u}$ อยู่ในนั้น เป็นแรงที่มาจาก pressure field ที่คำนวณแยก (pressure correction) จึงเป็น explicit term
</details>

<details>
<summary><b>3. SIMPLE กับ PISO ต่างกันอย่างไร?</b></summary>

- **SIMPLE**: วนซ้ำจนลู่เข้า ใช้กับ steady-state ต้องใช้ under-relaxation
- **PISO**: แก้ pressure หลายครั้งต่อ time step ใช้กับ transient ไม่ต้อง under-relax
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_Introduction.md](01_Introduction.md) — บทนำ FVM
- **บทถัดไป:** [03_Spatial_Discretization.md](03_Spatial_Discretization.md) — Spatial Discretization