# ภาพรวม Finite Volume Method

**Finite Volume Method (FVM)** เป็นวิธีการแปลงสมการ PDE ให้เป็นระบบสมการพีชคณิตที่คอมพิวเตอร์สามารถแก้ได้ FVM คือหัวใจของ OpenFOAM

---

## ทำไมต้องเข้าใจ FVM?

การเข้าใจ FVM ช่วยให้คุณ:
- เลือก **Discretization Schemes** ที่เหมาะสมใน `system/fvSchemes`
- แก้ปัญหา **Divergence** ได้โดยไม่ต้องลองผิดลองถูก
- ตรวจสอบ **Mesh Quality** ว่าเหมาะกับโจทย์หรือไม่
- อ่านและแก้ไข **Solver Source Code** ได้

---

## หลักการพื้นฐาน

### 1. Conservation Laws

FVM ทำงานบน **Integral form** ของสมการอนุรักษ์:

$$\frac{\partial}{\partial t}\int_V \phi\, dV + \oint_S \mathbf{F} \cdot \mathbf{n}\, dS = \int_V S\, dV$$

| สิ่งที่อนุรักษ์ | สมการ | OpenFOAM Field |
|----------------|-------|----------------|
| มวล | $\nabla \cdot \mathbf{u} = 0$ | `U`, `p` |
| โมเมนตัม | $\rho \frac{D\mathbf{u}}{Dt} = -\nabla p + \nabla \cdot \boldsymbol{\tau}$ | `U`, `p` |
| พลังงาน | $\rho c_p \frac{DT}{Dt} = k\nabla^2 T$ | `T` |

### 2. Control Volume Approach

โดเมนถูกแบ่งเป็น **Cells** ที่ไม่ทับซ้อนกัน:

```
Domain → Cells → Faces → Fluxes → Conservation
```

- ค่าตัวแปรเก็บที่ **Cell Centers**
- **Fluxes** คำนวณที่ **Faces**
- ผลรวม Flux = 0 (Conservation)

### 3. Discretization

แปลง Continuous → Discrete:

| Continuous | Discrete | OpenFOAM |
|-----------|----------|----------|
| $\frac{\partial \phi}{\partial t}$ | $\frac{\phi^{n+1} - \phi^n}{\Delta t}$ | `fvm::ddt(phi)` |
| $\nabla \cdot (\phi \mathbf{u})$ | $\sum_f \phi_f \Phi_f$ | `fvm::div(phi, U)` |
| $\nabla^2 \phi$ | $\sum_f \frac{\phi_N - \phi_P}{d_{PN}} S_f$ | `fvm::laplacian(D, phi)` |

---

## โครงสร้างบทเรียน

| ไฟล์ | เนื้อหา |
|------|---------|
| [01_Introduction.md](01_Introduction.md) | บทนำ FVM และหลักการ |
| [02_Fundamental_Concepts.md](02_Fundamental_Concepts.md) | Control Volume, Mesh |
| [03_Spatial_Discretization.md](03_Spatial_Discretization.md) | Gradient, Convection, Diffusion |
| [04_Temporal_Discretization.md](04_Temporal_Discretization.md) | Euler, Backward, CFL |
| [05_Matrix_Assembly.md](05_Matrix_Assembly.md) | สร้างระบบ [A][x]=[b] |
| [06_OpenFOAM_Implementation.md](06_OpenFOAM_Implementation.md) | fvMesh, fvMatrix, fvm/fvc |
| [07_Best_Practices.md](07_Best_Practices.md) | Mesh quality, Schemes |
| [08_Exercises.md](08_Exercises.md) | แบบฝึกหัด |

---

## Mapping สู่ OpenFOAM

| แนวคิด FVM | OpenFOAM File/Class | ตัวอย่าง |
|-----------|---------------------|---------|
| Control Volume | `constant/polyMesh/` | cells, faces, points |
| Field Values | `0/` directory | U, p, T |
| Discretization Schemes | `system/fvSchemes` | gradSchemes, divSchemes |
| Linear Solvers | `system/fvSolution` | PCG, GAMG, tolerances |
| P-V Coupling | `system/fvSolution` | SIMPLE, PISO, PIMPLE |

---

## สรุป

| จุดแข็ง FVM | ประโยชน์ |
|------------|---------|
| **Conservation** | มวล/พลังงานอนุรักษ์ในระดับ Cell |
| **Flexibility** | รองรับ Unstructured Mesh |
| **Robustness** | จัดการ Boundary Conditions ซับซ้อนได้ |
| **Efficiency** | Sparse Matrix → แก้ได้เร็ว |

---

## Concept Check

<details>
<summary><b>1. FVM ต่างจาก FDM (Finite Difference) อย่างไร?</b></summary>

FVM ทำงานบน **Integral form** ของสมการ จึงรับประกัน conservation โดยธรรมชาติ ส่วน FDM ทำงานบน differential form ซึ่งไม่รับประกัน conservation
</details>

<details>
<summary><b>2. ทำไมค่าตัวแปรเก็บที่ Cell Center ไม่ใช่ที่ Face?</b></summary>

เพราะ cell-centered approach ทำให้:
- จัดการ Boundary Conditions ง่าย
- รองรับ polyhedral mesh ได้
- Sparse matrix มีโครงสร้างดี
</details>

<details>
<summary><b>3. fvm กับ fvc ต่างกันอย่างไร?</b></summary>

- `fvm::` = **Implicit** — สร้าง matrix coefficient
- `fvc::` = **Explicit** — คำนวณค่าจาก field ปัจจุบัน
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [../01_GOVERNING_EQUATIONS/00_Overview.md](../01_GOVERNING_EQUATIONS/00_Overview.md) — สมการควบคุม
- **บทถัดไป:** [01_Introduction.md](01_Introduction.md) — บทนำ FVM