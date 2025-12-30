# ภาพรวม Boundary Conditions

## Learning Objectives

หลังจากศึกษาบทนี้ ผู้เรียนควรจะสามารถ:

1. **อธิบายความสำคัญของ Boundary Conditions (BC)** ในการแก้ปัญหา CFD และผลกระทบต่อความถูกต้องของผลลัพธ์
2. **จำแนกประเภทของ BC** ทั้ง 3 ประเภทหลัก (Dirichlet, Neumann, Robin) และเลือกใช้ OpenFOAM BC types ที่เหมาะสม
3. **ตั้งค่า BC ที่เหมาะสม** สำหรับ velocity, pressure, และ temperature ในสถานการณ์ต่างๆ
4. **ใช้หลักการ BC compatibility** ระหว่าง velocity และ pressure อย่างถูกต้อง
5. **หลีกเลี่ยงข้อผิดพลาดทั่วไป** ในการตั้งค่า BC ที่อาจทำให้การคำนวณ diverge

---

## 3W Framework

### What (อะไร) - Boundary Conditions คืออะไร?

**Boundary Conditions (BC)** คือการกำหนดพฤติกรรมของตัวแปร (velocity, pressure, temperature, ฯลฯ) ที่ขอบเขตของโดเมนคำนวณ ซึ่งประกอบด้วย 3 ประเภทหลัก:

| ประเภท | คณิตศาสตร์ | OpenFOAM Type | ใช้เมื่อ |
|--------|-----------|---------------|---------|
| **Dirichlet** | $\phi = \phi_0$ | `fixedValue` | กำหนดค่าตรงๆ (U inlet, T wall) |
| **Neumann** | $\frac{\partial \phi}{\partial n} = g$ | `fixedGradient`, `zeroGradient` | กำหนด flux หรือ fully developed |
| **Robin** | $\alpha\phi + \beta\frac{\partial\phi}{\partial n} = \gamma$ | `mixed` | Convective heat transfer |

### Why (ทำไม) - ทำไม BC ถึงสำคัญ?

> **BC คือสิ่งที่ทำให้โจทย์ปัญหาสมบูรณ์และมีคำตอบที่ถูกต้อง**

- **กำหนดปัญหาให้สมบูรณ์** — PDE ต้องมี BC จึงจะมี **unique solution** โดยเฉพาะอย่างยิ่งใน incompressible flow
- **ควบคุมพฤติกรรมการไหล** — Inlet, outlet, wall ต้องสะท้อน **physics จริง** มิฉะนั้นผลลัพธ์จะไม่มีความหมายทางฟิสิกส์
- **ส่งผลต่อ stability** — BC ที่ไม่สอดคล้องกันหรือขัดแย้งกันทำให้ **diverge** แม้ว่า discretization จะถูกต้อง
- **ส่งผลต่อความแม่นยำ** — BC ที่ไม่เหมาะสมสร้าง **boundary layer artifacts** หรือ unphysical reflections

### How (อย่างไร) - แนวทางการใช้งาน

**แนวทางการตั้งค่า BC ใน OpenFOAM:**

1. **เลือกประเภท BC** ตามสภาพฟิสิกส์ (Dirichlet/Neumann/Robin) → ดูตารางประเภทหลักด้านบน
2. **ตั้งค่า BC สำหรับแต่ละตัวแปร** (U, p, T, k, ε, ฯลฯ) → ดูตาราง BC ที่ใช้บ่อยด้านล่าง
3. **ตรวจสอบความสอดคล้อง** ระหว่าง velocity และ pressure → ดูหัวข้อ "ความสอดคล้องของ BC"
4. **ตรวจสอบ BC compatibility** 6 ข้อหลัก → ดูกฎเกณฑ์ในหัวข้อ "ข้อควรระวังเรื่อง BC Selection"
5. **แก้ปัญหา** หากเกิด divergence หรือผลลัพธ์แปลกปลอม → ดูไฟล์ [07_Troubleshooting_Boundary_Conditions.md](07_Troubleshooting_Boundary_Conditions.md)

---

## BC ที่ใช้บ่อยใน OpenFOAM

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

> **💡 ข้อควรระวังเรื่อง BC Selection:**
> 1. **Reference point:** ต้องมี p fixedValue อย่างน้อย 1 จุด → มิฉะนั้น pressure จะ drift
> 2. **Backflow:** Outlet ที่อาจมี backflow → ใช้ `inletOutlet` หรือ `pressureInletOutletVelocity`
> 3. **Compressibility:** Gas ที่ Ma > 0.3 → ใช้ `totalPressure` แทน `fixedValue`
> 4. **Wall functions:** Turbulent flow ต้องใช้ wall function BCs (kqRWallFunction, ฯลฯ)
> 5. **Initial conditions:** ต้อง consistent กับ BCs → ไม่งั้นอาจ diverge ตอนเริ่ม
> 6. **Physical constraints:** ค่าต้อง > 0 (k, ε, ω, nut) → ใช้ bounded schemes หรือตั้งค่าเริ่มต้นให้เหมาะสม

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

## Key Takeaways

✅ **Boundary Conditions คือหัวใจของการแก้ปัญหา CFD** — ไม่ว่า discretization จะดีแค่ไหน ถ้า BC ผิด ผลลัพธ์ก็จะผิด

✅ **3 ประเภทหลัก:** Dirichlet (กำหนดค่า), Neumann (กำหนด gradient), Robin (ผสมทั้งสอง) — แต่ละประเภทมี use case ที่แตกต่างกัน

✅ **ความสอดคล้องของ BC สำคัญมาก** — โดยเฉพาะ coupling ระหว่าง velocity และ pressure (fixedValue ↔ zeroGradient)

✅ **ต้องมี reference pressure อย่างน้อย 1 จุด** — มิฉะนั้น pressure จะ drift ใน incompressible flow

✅ **BC selection ต้องคำนึงถึง:** compressibility, backflow, turbulence, initial conditions, และ physical constraints

✅ **BC ที่ไม่ถูกต้องเป็นสาเหตุหลักของ divergence** — ตรวจสอบ BC ก่อนเสมอเมื่อเจอปัญหา convergence

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [../02_FINITE_VOLUME_METHOD/00_Overview.md](../02_FINITE_VOLUME_METHOD/00_Overview.md) — Finite Volume Method
- **บทถัดไป:** [01_Introduction.md](01_Introduction.md) — บทนำ Boundary Conditions