# ประเด็นสำคัญที่ควรจดจำ

เอกสารนี้สรุปแนวคิดหลักจากบทสมการควบคุม

> **ทำไมต้องอ่านบทสรุปนี้?**
> - **Quick reference** สำหรับทบทวนก่อนทำงานจริง
> - รวมทุกสิ่งที่ต้องรู้ใน **1 หน้า**
> - มี **checklist** พร้อมใช้งาน

---

---

## 1. กฎการอนุรักษ์

CFD ทั้งหมดสร้างบนหลักการอนุรักษ์ 3 ข้อ:

| กฎ | สมการ | ความหมาย |
|----|-------|----------|
| **มวล** | $\nabla \cdot \mathbf{u} = 0$ | ไหลเข้า = ไหลออก |
| **โมเมนตัม** | $\rho \frac{D\mathbf{u}}{Dt} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$ | แรง = มวล × ความเร่ง |
| **พลังงาน** | $\rho c_p \frac{DT}{Dt} = k \nabla^2 T + Q$ | พลังงานไม่สูญหาย |

### สมการการขนส่งทั่วไป

$$\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \phi \mathbf{u}) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi$$

นี่คือ template ที่ OpenFOAM ใช้ discretize ทุกสมการ

---

## 2. Pressure-Velocity Coupling

ในการไหล incompressible ความดันไม่ได้มาจาก EOS แต่ทำหน้าที่ **บังคับให้ $\nabla \cdot \mathbf{u} = 0$**

| Algorithm | ประเภท | ใช้เมื่อ |
|-----------|--------|---------|
| **SIMPLE** | Steady-state | ไม่สนใจ transient |
| **PISO** | Transient | $\Delta t$ เล็ก |
| **PIMPLE** | Transient | $\Delta t$ ใหญ่ |

---

## 3. สมการสถานะ (EOS)

EOS เชื่อมโยง $p$, $\rho$, $T$ และกำหนดประเภทการไหล:

| EOS | สมการ | Solver |
|-----|-------|--------|
| Ideal Gas | $p = \rho R T$ | `rhoSimpleFoam` |
| Incompressible | $\rho = \text{const}$ | `simpleFoam` |

**กฎ Mach Number:**
- $Ma < 0.3$ → Incompressible
- $Ma > 0.3$ → Compressible

---

## 4. เลขไร้มิติ

| เลข | สูตร | บอกอะไร |
|-----|------|---------|
| **Reynolds** | $Re = \rho UL/\mu$ | Laminar vs Turbulent |
| **Mach** | $Ma = U/c$ | Incomp vs Comp |
| **Froude** | $Fr = U/\sqrt{gL}$ | Free surface regime |
| **Prandtl** | $Pr = c_p\mu/k$ | Thermal BL thickness |

### Flow Regime จาก Re

| Re | ระบอบ | Turbulence Model |
|----|-------|------------------|
| < 2300 | Laminar | `laminar` |
| 2300-4000 | Transitional | — |
| > 4000 | Turbulent | `kEpsilon`, `kOmegaSST` |

---

## 5. การแปลสมการ → OpenFOAM

| คณิตศาสตร์ | OpenFOAM Function | ไฟล์ควบคุม |
|-----------|-------------------|-----------|
| $\frac{\partial \phi}{\partial t}$ | `fvm::ddt(phi)` | `ddtSchemes` |
| $\nabla \cdot (\phi \mathbf{u})$ | `fvm::div(phi, U)` | `divSchemes` |
| $\nabla^2 \phi$ | `fvm::laplacian(D, phi)` | `laplacianSchemes` |
| $\nabla p$ | `fvc::grad(p)` | `gradSchemes` |

### ความแตกต่าง fvm vs fvc

| Prefix | ประเภท | ผลลัพธ์ |
|--------|--------|--------|
| `fvm::` | Implicit | เข้า matrix |
| `fvc::` | Explicit | คำนวณทันที |

---

## 6. Boundary Conditions

| ประเภท | OpenFOAM | ใช้กับ |
|--------|----------|--------|
| Dirichlet | `fixedValue` | Inlet U, Wall T |
| Neumann | `zeroGradient` | Outlet U, Wall p |
| Mixed | `inletOutlet` | Outlet ที่อาจมี backflow |

### การจับคู่มาตรฐาน

| ตำแหน่ง | U | p |
|---------|---|---|
| Inlet | `fixedValue` | `zeroGradient` |
| Outlet | `zeroGradient` | `fixedValue` |
| Wall | `noSlip` | `zeroGradient` |

---

## 7. Initial Conditions

- กำหนดใน `internalField` ของไฟล์ `0/`
- สำหรับ **steady-state**: ค่าประมาณก็พอ (solver จะวนซ้ำ)
- สำหรับ **transient**: ต้องตรงกับ physics ที่ $t=0$

> ⚠️ อย่าใส่ k, epsilon = 0 (จะ divide by zero)

---

## 8. Wall Treatment

| $y^+$ Range | บริเวณ | วิธีจัดการ |
|-------------|--------|-----------|
| $y^+ < 5$ | Viscous sublayer | Resolve (low-Re model) |
| $30 < y^+ < 300$ | Log-law | Wall function |

ตรวจสอบด้วย:
```bash
postProcess -func yPlus
```

---

## 9. โครงสร้าง Case Directory

```
case/
├── 0/                  # Initial & Boundary Conditions
│   ├── U               # Velocity
│   ├── p               # Pressure
│   └── k, epsilon      # Turbulence
├── constant/           # Physics & Mesh
│   ├── transportProperties
│   ├── turbulenceProperties
│   └── polyMesh/
└── system/             # Numerics & Control
    ├── controlDict     # Time stepping
    ├── fvSchemes       # Discretization
    └── fvSolution      # Solvers & algorithms
```

---

## 10. Checklist ก่อนรัน

- [ ] $Ma < 0.3$? → ใช้ incompressible solver
- [ ] $Re > 4000$? → เปิด turbulence model
- [ ] Inlet: $U$ fixed, $p$ zeroGradient?
- [ ] Outlet: $U$ zeroGradient, $p$ fixed?
- [ ] Wall: $U$ noSlip, wall functions ถ้า turbulent?
- [ ] k, epsilon ≠ 0?
- [ ] Mesh y+ ตรงกับ wall treatment?

---

## Concept Check

<details>
<summary><b>1. ทำไมต้องเข้าใจสมการควบคุมก่อนใช้ OpenFOAM?</b></summary>

เพราะทุกการตั้งค่าใน OpenFOAM (schemes, BCs, solver) มาจากสมการเหล่านี้ ถ้าไม่เข้าใจ จะแก้ปัญหา divergence หรือผลลัพธ์ผิดพลาดไม่ได้
</details>

<details>
<summary><b>2. SIMPLE กับ PIMPLE ต่างกันอย่างไร?</b></summary>

- **SIMPLE** = Steady-state, วนซ้ำจนลู่เข้า
- **PIMPLE** = Transient, รองรับ $\Delta t$ ใหญ่ได้ด้วย outer corrections
</details>

<details>
<summary><b>3. fvm::div กับ fvc::div ต่างกันอย่างไร?</b></summary>

- `fvm::div` = Implicit, สร้าง matrix coefficient
- `fvc::div` = Explicit, คำนวณค่าทันทีจาก field ปัจจุบัน
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [07_Initial_Conditions.md](07_Initial_Conditions.md) — เงื่อนไขเริ่มต้น
- **บทถัดไป:** [09_Exercises.md](09_Exercises.md) — แบบฝึกหัด
- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวมบทนี้
