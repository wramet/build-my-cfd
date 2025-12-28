# ภาพรวม Boundary Conditions

**Boundary Conditions (BC)** กำหนดพฤติกรรมของตัวแปรที่ขอบเขตของโดเมน

> **ทำไม BC ถึงสำคัญที่สุด?**
> - **กำหนดปัญหาให้สมบูรณ์** — PDE ต้องมี BC จึงจะมี unique solution
> - **ควบคุมพฤติกรรมการไหล** — Inlet, outlet, wall ต้องสะท้อน physics จริง
> - **ส่งผลต่อ stability** — BC ที่ไม่สอดคล้องกันทำให้ diverge

---

## ประเภทหลักของ BC

| ประเภท | คณิตศาสตร์ | OpenFOAM Type | ใช้เมื่อ |
|--------|-----------|---------------|---------|
| **Dirichlet** | $\phi = \phi_0$ | `fixedValue` | กำหนดค่าตรงๆ (U inlet, T wall) |
| **Neumann** | $\frac{\partial \phi}{\partial n} = g$ | `fixedGradient`, `zeroGradient` | กำหนด flux หรือ fully developed |
| **Robin** | $\alpha\phi + \beta\frac{\partial\phi}{\partial n} = \gamma$ | `mixed` | Convective heat transfer |

---

## BC ที่ใช้บ่อย

### Velocity (U)

| Location | Type | ตั้งค่า |
|----------|------|---------|
| Inlet | `fixedValue` | `uniform (10 0 0)` |
| Outlet | `zeroGradient` หรือ `pressureInletOutletVelocity` | — |
| Wall | `noSlip` | — |

### Pressure (p)

| Location | Type | ตั้งค่า |
|----------|------|---------|
| Inlet | `zeroGradient` | — |
| Outlet | `fixedValue` | `uniform 0` |
| Wall | `zeroGradient` | — |

### Temperature (T)

| Location | Type | ตั้งค่า |
|----------|------|---------|
| Inlet | `fixedValue` | `uniform 300` |
| Outlet | `zeroGradient` | — |
| Fixed T wall | `fixedValue` | `uniform 350` |
| Adiabatic wall | `zeroGradient` | — |
| Heat flux wall | `fixedGradient` | `uniform 1000` |

---

## ความสอดคล้องของ BC

> ⚠️ **กฎสำคัญ:** ถ้ากำหนด U เป็น `fixedValue` ต้องกำหนด p เป็น `zeroGradient` (และกลับกัน)

| U Type | p Type | ตัวอย่าง |
|--------|--------|---------|
| `fixedValue` | `zeroGradient` | Velocity inlet |
| `zeroGradient` | `fixedValue` | Pressure outlet |
| `noSlip` | `zeroGradient` | Wall |

---

## โครงสร้างบทเรียน

| ไฟล์ | เนื้อหา |
|------|---------| 
| [01_Introduction.md](01_Introduction.md) | บทนำและหลักการ |
| [02_Fundamental_Classification.md](02_Fundamental_Classification.md) | Dirichlet, Neumann, Robin |
| [03_Selection_Guide_Which_BC_to_Use.md](03_Selection_Guide_Which_BC_to_Use.md) | Decision tree สำหรับเลือก BC |
| [04_Mathematical_Formulation.md](04_Mathematical_Formulation.md) | สูตรทางคณิตศาสตร์ |
| [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md) | BC ที่ใช้บ่อยใน OpenFOAM |
| [06_Advanced_Boundary_Conditions.md](06_Advanced_Boundary_Conditions.md) | Wall functions, Time-varying, Coupled |
| [07_Troubleshooting_Boundary_Conditions.md](07_Troubleshooting_Boundary_Conditions.md) | การแก้ปัญหา |
| [08_Exercises.md](08_Exercises.md) | แบบฝึกหัด |

---

## OpenFOAM Files

| File | เนื้อหา |
|------|---------| 
| `0/U` | Velocity BC |
| `0/p` | Pressure BC |
| `0/T` | Temperature BC |
| `0/k`, `0/epsilon`, `0/omega` | Turbulence BC |
| `constant/polyMesh/boundary` | Patch names และ types |

---

## Concept Check

<details>
<summary><b>1. Dirichlet กับ Neumann ต่างกันอย่างไร?</b></summary>

- **Dirichlet**: กำหนด **ค่า** ที่ขอบ ($\phi = \phi_0$)
- **Neumann**: กำหนด **gradient/flux** ที่ขอบ ($\frac{\partial\phi}{\partial n} = g$)
</details>

<details>
<summary><b>2. ทำไมต้องกำหนด reference pressure?</b></summary>

ใน incompressible flow สมการสนใจเฉพาะ $\nabla p$ ไม่ใช่ค่าสัมบูรณ์ → ต้องกำหนดจุดอ้างอิง (เช่น outlet p=0) เพื่อให้ solution เป็น unique
</details>

<details>
<summary><b>3. zeroGradient หมายความว่าอะไร?</b></summary>

$\frac{\partial\phi}{\partial n} = 0$ → ค่าไม่เปลี่ยนแปลงในทิศทางตั้งฉากกับขอบ → ใช้สำหรับ fully developed flow หรือ adiabatic wall
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [../02_FINITE_VOLUME_METHOD/00_Overview.md](../02_FINITE_VOLUME_METHOD/00_Overview.md) — Finite Volume Method
- **บทถัดไป:** [01_Introduction.md](01_Introduction.md) — บทนำ Boundary Conditions