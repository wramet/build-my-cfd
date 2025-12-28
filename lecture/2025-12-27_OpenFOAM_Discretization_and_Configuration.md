# บันทึกบทเรียน: OpenFOAM Discretization และ Configuration

**วันที่:** 27 ธันวาคม 2025

> **สิ่งที่จะได้เรียนรู้:**
> 1. แปลงสมการฟิสิกส์เป็นโค้ด
> 2. ตั้งค่า `fvSchemes` และ `fvSolution`
> 3. เขียน `createFields.H`

---

## 1. 3 สมการหลักของ CFD

> ทุกอย่างใน OpenFOAM เริ่มจาก 3 สมการนี้ — ถ้าเข้าใจสมการ จะเข้าใจ solver

### 1.1 การอนุรักษ์มวล (Continuity)

**Physics:** มวลไม่หายไปไหน — ไหลเข้า = ไหลออก

$$\nabla \cdot \mathbf{u} = 0 \quad \text{(incompressible)}$$

```cpp
fvc::div(phi)  // ตรวจสอบว่า = 0
```

**ทำไมสำคัญ?**
- สมการนี้ไม่ได้ "แก้" โดยตรง แต่ใช้เป็น **constraint** สร้างสมการความดัน
- ถ้า continuity error สูง = มวลหายไปในการคำนวณ → ผลลัพธ์ไม่น่าเชื่อถือ

---

### 1.2 การอนุรักษ์โมเมนตัม (Navier-Stokes)

**Physics:** F = ma — แรงทำให้ของไหลเร่ง

$$\underbrace{\frac{\partial \mathbf{u}}{\partial t}}_{\text{เปลี่ยนตามเวลา}} + \underbrace{(\mathbf{u} \cdot \nabla)\mathbf{u}}_{\text{ของไหลพาตัวเอง}} = \underbrace{-\frac{1}{\rho}\nabla p}_{\text{ความดันดัน}} + \underbrace{\nu\nabla^2\mathbf{u}}_{\text{ความหนืดยับยั้ง}}$$

```cpp
fvVectorMatrix UEqn
(
    fvm::ddt(U)           // ∂u/∂t
  + fvm::div(phi, U)      // (u·∇)u
  - fvm::laplacian(nu, U) // ν∇²u
);
solve(UEqn == -fvc::grad(p));
```

**แต่ละเทอมหมายความว่าอะไร?**

| เทอม | ความหมาย | OpenFOAM | อธิบาย |
|------|----------|----------|--------|
| `ddt` | เปลี่ยนตามเวลา | `fvm::ddt(U)` | ความเร็วเปลี่ยนจาก time step ก่อน |
| `div` | Convection | `fvm::div(phi, U)` | ของไหลพาโมเมนตัมไปด้วย (ทำให้เกิด non-linear!) |
| `laplacian` | Diffusion | `fvm::laplacian(nu, U)` | ความหนืดทำให้โมเมนตัมกระจาย (เป็นตัวทำให้เสถียร) |
| `grad` | Pressure | `fvc::grad(p)` | ความดันดันของไหลจากที่สูงไปต่ำ |

**ทำไม Convection ถึงยากที่สุด?**
- เทอม $(u \cdot \nabla)u$ มี **ความเร็วคูณความเร็ว** → Non-linear!
- ค่าสามารถกระโดดสูงมาก (unbounded) → ระเบิดได้
- ต้องเลือก discretization scheme อย่างระมัดระวัง

---

### 1.3 การอนุรักษ์พลังงาน

**Physics:** พลังงานไม่หาย เพียงเปลี่ยนรูป

$$\rho c_p \frac{DT}{Dt} = k \nabla^2 T + Q$$

```cpp
fvm::ddt(T) + fvm::div(phi, T) - fvm::laplacian(alpha, T)
```

**ใช้เมื่อไหร่?**
- ❌ น้ำไหลในท่อ (isothermal) — ไม่ต้องแก้ เพราะอุณหภูมิไม่เปลี่ยน
- ✅ Heat transfer — ต้องแก้ เพื่อหาการกระจายอุณหภูมิ
- ✅ Compressible flow — ต้องแก้ เพราะ $\rho = \rho(p, T)$

---

## 2. เลือก Solver: Re และ Ma

> **ก่อนเริ่ม simulation ต้องคำนวณ Re และ Ma เสมอ!**

### Reynolds Number (Re) — บอก Laminar vs Turbulent

$$Re = \frac{UL}{\nu} = \frac{\text{Inertia forces}}{\text{Viscous forces}}$$

**ทำไมสำคัญ?**
- Re ต่ำ: ความหนืดชนะ → flow เรียบ (laminar)
- Re สูง: inertia ชนะ → flow ปั่นป่วน (turbulent) → ต้องใช้ turbulence model

| Re | Flow | Solver | เหตุผล |
|----|------|--------|--------|
| < 2300 | Laminar | `icoFoam` | ไม่ต้องมี turbulence model |
| > 4000 | Turbulent | `simpleFoam` + k-ε | ต้อง model eddies ที่มองไม่เห็น |

### Mach Number (Ma) — บอก Incompressible vs Compressible

$$Ma = \frac{U}{c} = \frac{\text{Flow speed}}{\text{Sound speed}}$$

**ทำไมสำคัญ?**
- Ma < 0.3: ความหนาแน่นเกือบคงที่ → ใช้สมการง่ายกว่า
- Ma > 0.3: ความหนาแน่นเปลี่ยน → ต้องแก้สมการ state ($p = \rho RT$)

| Ma | Flow | Solver | เหตุผล |
|----|------|--------|--------|
| < 0.3 | Incompressible | `simpleFoam` | $\rho$ = constant, ง่ายกว่า |
| > 0.3 | Compressible | `rhoSimpleFoam` | ต้องคิด $\rho(p,T)$ |

---

## 3. fvSchemes — การแปลงสมการ

> **หน้าที่:** แปลง Calculus (สมการอนุพันธ์) → Algebra (สมการเชิงเส้น Ax=b)

### 3.1 ปัญหาหลัก: ค่าเก็บที่ไหน?

```
OpenFOAM เก็บค่า (p, U, T) ที่: Cell Center (จุดกลางเซลล์)
แต่ FVM ต้องคำนวณ flux ที่: Face (ผิวหน้าระหว่างเซลล์)
```

**ปัญหา:** เราไม่รู้ค่าที่ face → ต้อง **interpolate** จาก cell center

**ทางออก:** ใช้ Schemes เพื่อ "เดา" ค่าที่ face จากค่าที่ cell center

---

### 3.2 divSchemes (Convection) — สำคัญที่สุด!

**โจทย์:** เลือกวิธี interpolate จาก cell center ไป face สำหรับเทอม $\nabla \cdot (u\phi)$

#### Scheme 1: Upwind — เสถียรแต่เบลอ

```
Face value = ค่าจากฝั่งต้นลม (upwind cell)
```

**ทำไมเสถียร?** เพราะค่าไม่มีทางเกินค่าที่ cell center → Bounded

**ทำไมเบลอ?** เพราะเป็น 1st order accuracy → numerical diffusion สูง (เหมือนภาพไม่ชัด)

#### Scheme 2: Linear (Central) — แม่นยำแต่ระเบิดง่าย

```
Face value = เฉลี่ยจากทั้ง 2 ฝั่ง
```

**ทำไมแม่นยำ?** เพราะเป็น 2nd order accuracy

**ทำไมระเบิด?** เพราะค่าอาจเกินค่าที่ cell center (overshoot) → Unbounded → oscillation → blow up

#### Scheme 3: LinearUpwind — สมดุล (แนะนำ)

```
Face value = Upwind + gradient correction
```

**ทำไมดี?** ได้ทั้งความแม่นยำ (2nd order) และความเสถียร (bounded)

| Scheme | ข้อดี | ข้อเสีย | ใช้เมื่อ |
|--------|------|--------|---------|
| `Gauss upwind` | เสถียรมาก | เบลอ (numerical diffusion) | เริ่มต้น, flow รุนแรง |
| `Gauss linear` | แม่นยำ (2nd order) | ระเบิดง่าย (oscillation) | flow สงบมาก |
| `Gauss linearUpwind` | สมดุล | - | **แนะนำสำหรับ production** |

```cpp
divSchemes
{
    default         none;
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,k)      Gauss upwind;  // turbulence ใช้ upwind เพราะ sensitive
}
```

> **กลยุทธ์:** เริ่มด้วย `upwind` จนเสถียร แล้วค่อยเปลี่ยนเป็น `linearUpwind` เพื่อความแม่นยำ

---

### 3.3 laplacianSchemes (Diffusion) — จัดการ Mesh เบี้ยว

**โจทย์:** คำนวณ $\nabla \cdot (\Gamma \nabla \phi)$ ต้องหา gradient ที่ face

**ปัญหา:** ถ้า mesh เบี้ยว (non-orthogonal) การคำนวณ gradient จะผิด!

#### ทำไม Mesh เบี้ยวถึงเป็นปัญหา?

```
Mesh สวย (orthogonal):
  เส้นเชื่อม cell centers ตั้งฉากกับ face → คำนวณ gradient ง่าย

Mesh เบี้ยว (non-orthogonal):
  เส้นเชื่อมไม่ตั้งฉาก → gradient ที่คำนวณเพี้ยน → ต้องมี correction term
```

| Mesh Quality | Scheme | เหตุผล |
|--------------|--------|--------|
| สวย (orthogonal) | `Gauss linear uncorrected` | ไม่ต้อง correct, เร็วที่สุด |
| ปกติ (< 70°) | `Gauss linear corrected` | มี correction term แก้ความเพี้ยน |
| เบี้ยวมาก (> 70°) | `Gauss linear limited 0.5` | correct แบบยั้งๆ ไม่งั้นระเบิด |

```cpp
laplacianSchemes
{
    default         Gauss linear corrected;
}
```

> **เช็ค mesh:** `checkMesh` → ดู "max non-orthogonality"
> - < 70° → ใช้ `corrected`
> - > 70° → ใช้ `limited` หรือแก้ mesh

---

### 3.4 ddtSchemes (Time) — Implicit vs Explicit

**โจทย์:** แปลง $\frac{\partial \phi}{\partial t}$ เป็น finite difference

#### Euler Implicit (1st order)

$$\frac{\phi^{n+1} - \phi^n}{\Delta t}$$

**ทำไมเสถียร?** เพราะใช้ค่า $\phi^{n+1}$ (ค่าใหม่ที่กำลังหา) → ค่า coefficient ใน matrix ใหญ่ → Diagonal dominant → Solver แก้ง่าย

**ทำไมเบลอ?** เพราะ 1st order → numerical diffusion

#### Backward (2nd order)

$$\frac{3\phi^{n+1} - 4\phi^n + \phi^{n-1}}{2\Delta t}$$

**ทำไมแม่นยำกว่า?** ใช้ข้อมูลจาก 2 time steps ก่อนหน้า → 2nd order accurate

| Scheme | Order | เสถียร | แม่นยำ | ใช้เมื่อ |
|--------|-------|--------|--------|---------|
| `Euler` | 1st | ✅✅ | ❌ | เริ่มต้น, ต้องการเสถียร |
| `backward` | 2nd | ✅ | ✅ | ต้องการความแม่นยำทางเวลา |

---

## 4. fvSolution — การแก้สมการ

> **หน้าที่:** แก้ระบบ Ax = b ที่ได้จาก fvSchemes

### 4.1 เลือก Linear Solver

**ปัญหา:** Matrix A ใน CFD มีขนาดใหญ่มาก (ล้าน x ล้าน) → ใช้ direct solver ไม่ได้ → ต้องใช้ iterative solver

#### ทำไมต้องดูว่า Matrix สมมาตรไหม?

- **Symmetric matrix:** ใช้ `PCG` (Conjugate Gradient) — algorithm optimize สำหรับ symmetric
- **Asymmetric matrix:** ใช้ `PBiCGStab` — รองรับ asymmetric

| สมการ | Matrix Type | Solver | เหตุผล |
|-------|-------------|--------|--------|
| Pressure (Laplacian) | Symmetric | `PCG` | $\nabla^2 p$ สมมาตร |
| Velocity (Convection) | Asymmetric | `PBiCGStab` | $(u \cdot \nabla)u$ ทำให้ asymmetric |

```cpp
solvers
{
    p
    {
        solver          PCG;
        preconditioner  DIC;       // ช่วยให้ converge เร็วขึ้น
        tolerance       1e-06;     // หยุดเมื่อ residual < 1e-6
        relTol          0.01;      // หยุดเมื่อลดลง 100 เท่า
    }
    U
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-05;
        relTol          0.1;
    }
}
```

#### tolerance vs relTol

- **tolerance (absolute):** หยุดเมื่อ residual < ค่านี้
- **relTol (relative):** หยุดเมื่อ residual ลดลงจากตอนเริ่มต้นตามสัดส่วนนี้

> สำหรับ transient: ใช้ `relTol 0` เพื่อให้แก้จน tolerance เสมอ (ทุก time step ต้องแม่น)

---

### 4.2 P-V Coupling Algorithm

**ปัญหา:** สมการ momentum ต้องใช้ p, แต่สมการ pressure ต้องใช้ U → งูกินหาง!

**ทางออก:** ใช้ algorithm แบบ iterative

#### SIMPLE (Steady-state)

```
Loop จนกว่าจะ converge:
  1. แก้สมการ U (ใช้ p จาก iteration ก่อน)
  2. แก้สมการ p (บังคับ continuity)
  3. แก้ U อีกทีด้วย p ใหม่
```

**ทำไมใช้กับ steady?** เพราะเราไม่สนใจความแม่นยำระหว่างทาง สนแค่ตอนจบ

#### PISO (Transient)

```
ทุก time step:
  1. แก้สมการ U
  2. แก้สมการ p (วนซ้ำ nCorrectors รอบ)
  3. แก้ U ด้วย p ใหม่
```

**ทำไมต้องวนหลายรอบ?** เพราะทุก time step ต้องแม่นยำ (ไม่เหมือน SIMPLE ที่รอ converge ตอนจบ)

#### PIMPLE (Transient + Large Δt)

```
ทุก time step:
  วน SIMPLE loop (nOuterCorrectors รอบ):
    วน PISO loop (nCorrectors รอบ)
```

**ทำไมดีกว่า PISO?** สามารถใช้ Δt ใหญ่ขึ้นได้ เพราะมี outer loop ช่วยเสถียร

| Type | Algorithm | ใช้เมื่อ |
|------|-----------|---------|
| Steady | `SIMPLE` | ภาพนิ่ง, ไม่สนใจ transient |
| Transient | `PISO` | Δt เล็ก, ต้องการความแม่นทุก step |
| Transient | `PIMPLE` | Δt ใหญ่, ยอมเสียเวลาคำนวณ |

---

## 5. fvm vs fvc — ความแตกต่างสำคัญ

> **กฎทอง:** Unknown → `fvm::`, Known → `fvc::`

### ทำไมต้องแยก?

- **`fvm::`** (Finite Volume **Method**): สร้าง **coefficient** ใน matrix A
  - ผลลัพธ์: Implicit → เสถียร แต่ต้องแก้ Ax=b
  
- **`fvc::`** (Finite Volume **Calculus**): คำนวณ **ค่าตัวเลข** เลย
  - ผลลัพธ์: Explicit → เร็ว แต่อาจไม่เสถียร

### ตัวอย่างเข้าใจง่าย

```cpp
// สมมติกำลังแก้หา U (unknown)
fvVectorMatrix UEqn
(
    fvm::ddt(U)              // U คือ unknown → ใส่ใน matrix
  + fvm::div(phi, U)         // U คือ unknown → ใส่ใน matrix
  - fvm::laplacian(nu, U)    // U คือ unknown → ใส่ใน matrix
);

// p รู้ค่าแล้ว (จาก iteration ก่อน) → คำนวณเลย
solve(UEqn == -fvc::grad(p)); 
```

**ถ้าใช้ผิดล่ะ?**
- ใช้ `fvc::` กับ unknown → Explicit → ต้องใช้ Δt เล็กมากไม่งั้นระเบิด!
- ใช้ `fvm::` กับ known → ไม่ผิด แต่ไม่จำเป็น (เสียเวลา compile)

> **จำง่าย:** fv**M** = **M**atrix, fv**C** = **C**alculate now

---

## 6. createFields.H — สร้างตัวแปร

### 6.1 โครงสร้างพื้นฐาน

```cpp
volScalarField p     // Scalar ที่ cell center
(
    IOobject
    (
        "p",                     // ชื่อไฟล์ (ต้องตรงกับ 0/p)
        runTime.timeName(),      // โฟลเดอร์ (0, 0.5, ...)
        mesh,
        IOobject::MUST_READ,     // ต้องอ่านจากไฟล์
        IOobject::AUTO_WRITE     // เขียนอัตโนมัติตาม writeInterval
    ),
    mesh
);
```

### 6.2 ประเภท Field

| Type | เก็บที่ | ตัวอย่าง | ทำไมต้องแยก? |
|------|--------|---------|-------------|
| `volScalarField` | Cell center | p, T, k | ค่า intensive (ไม่ขึ้นกับขนาด) |
| `volVectorField` | Cell center | U | ความเร็วเป็น vector |
| `surfaceScalarField` | Face | phi | flux ต้องเก็บที่ face เพราะ FVM ทำงานที่ face |

### 6.3 IO Options

| Read | เมื่อไหร่ | ตัวอย่าง |
|------|---------|---------|
| `MUST_READ` | ต้องมีไฟล์ ไม่งั้น error | p, U (ตัวแปรหลัก) |
| `READ_IF_PRESENT` | มีก็อ่าน ไม่มีใช้ default | phi (สร้างจาก U ได้) |
| `NO_READ` | ไม่ต้องมีไฟล์ | ตัวแปรชั่วคราวในการคำนวณ |

---

## 7. Quick Reference

### fvSchemes Template

```cpp
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }

ddtSchemes { default Euler; }              // เวลา

gradSchemes { default Gauss linear; }      // gradient

divSchemes                                  // convection (สำคัญ!)
{
    default         none;
    div(phi,U)      Gauss linearUpwind grad(U);  // แนะนำ
    div(phi,k)      Gauss upwind;                // turbulence ใช้ upwind
    div(phi,epsilon) Gauss upwind;
}

laplacianSchemes { default Gauss linear corrected; }  // diffusion

interpolationSchemes { default linear; }

snGradSchemes { default corrected; }
```

### fvSolution Template

```cpp
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }

solvers
{
    p { solver PCG; preconditioner DIC; tolerance 1e-06; relTol 0.01; }
    U { solver PBiCGStab; preconditioner DILU; tolerance 1e-05; relTol 0.1; }
}

SIMPLE
{
    nNonOrthogonalCorrectors 1;  // เพิ่มถ้า mesh เบี้ยว
    residualControl { p 1e-4; U 1e-4; }
}

relaxationFactors  // ช่วยเสถียร (SIMPLE only)
{
    fields { p 0.3; }
    equations { U 0.7; k 0.7; }
}
```

---

## 8. Common Problems & Solutions

| ปัญหา | ทำไมเกิด | แก้ไขอย่างไร |
|-------|---------|-------------|
| **ระเบิด (Blow up)** | Δt ใหญ่เกิน หรือ scheme ไม่เสถียร | ลด Δt, เปลี่ยนเป็น `upwind` |
| **Residual ไม่ลง** | Mesh ไม่ดี หรือ BCs ขัดแย้ง | `checkMesh`, ตรวจ BCs |
| **ผลเบลอ** | ใช้ `upwind` (1st order) | เปลี่ยนเป็น `linearUpwind` |
| **Continuity error สูง** | P-V coupling ไม่ดี | เพิ่ม `nCorrectors` |
| **Converge ช้า** | Relaxation สูงเกิน | ลด relaxation factors |

---

## 9. Workflow สรุป

```
1. คำนวณ Re, Ma → เลือก Solver
2. สร้าง mesh → checkMesh (ดู non-orthogonality)
3. ตั้งค่า 0/ → p, U, BCs
4. ตั้งค่า constant/ → transportProperties
5. ตั้งค่า system/fvSchemes → เริ่มด้วย upwind
6. ตั้งค่า system/fvSolution → SIMPLE/PISO/PIMPLE
7. รัน → simpleFoam > log 2>&1 &
8. Monitor → tail -f log | grep Residual
9. ถ้าเสถียร → เปลี่ยน scheme เป็น linearUpwind
```

---

## 10. Decision Trees

### เลือก Solver

```
คำนวณ Re = UL/ν

Re < 2300? 
  → icoFoam (laminar, transient)

Re > 4000?
  → คำนวณ Ma = U/c
      Ma < 0.3?
        → Steady? → simpleFoam
        → Transient? → pimpleFoam
      Ma > 0.3?
        → rhoSimpleFoam / sonicFoam
```

### เลือก divSchemes

```
Simulation เพิ่งเริ่ม?
  → Gauss upwind (เสถียร, ยอมเบลอ)

เสถียรแล้ว ต้องการความแม่นยำ?
  → Gauss linearUpwind grad(phi);

Flow สงบมาก ไม่มี shock?
  → Gauss linear (แม่นยำสุด)
```

### เลือก Algorithm

```
Steady-state (ไม่สนใจ transient)?
  → SIMPLE + relaxation factors

Transient + Δt เล็ก (Co < 1)?
  → PISO + nCorrectors 2-3

Transient + Δt ใหญ่ (Co > 1)?
  → PIMPLE + nOuterCorrectors 2-3
```

---

## 11. สรุปท้ายบท

### หลักการ 3 ข้อจำง่าย

1. **fvSchemes ควบคุมความแม่นยำ**
   - `upwind` = เสถียร แต่เบลอ
   - `linear` = แม่นยำ แต่ระเบิดง่าย
   - `linearUpwind` = สมดุล

2. **fvSolution ควบคุมความเสถียร**
   - SIMPLE = steady (วนจนนิ่ง)
   - PISO = transient (ทุก step ต้องแม่น)
   - PIMPLE = transient + Δt ใหญ่

3. **fvm vs fvc**
   - fvm = สร้าง matrix (implicit, เสถียร)
   - fvc = คำนวณค่า (explicit, เร็ว)

---

*"เริ่มด้วยเสถียร (upwind, SIMPLE) แล้วค่อยเพิ่มความแม่นยำ (linearUpwind)"*

---

## 12. 🧠 Advanced Concept Check

> **คำเตือน:** คำถามเหล่านี้ต้องการความเข้าใจลึก ไม่ใช่แค่ท่องจำ

### Level 1: Foundation Understanding

<details>
<summary><b>Q1: ทำไม Convection term ถึงทำให้ Matrix เป็น Asymmetric?</b></summary>

**คำตอบ:**

พิจารณา 1D convection: $u \frac{\partial \phi}{\partial x}$

เมื่อ discretize ด้วย upwind:
$$u \frac{\partial \phi}{\partial x} \approx u \frac{\phi_P - \phi_W}{\Delta x}$$

**Coefficient ที่ได้:**
- Cell P ได้: $+u/\Delta x$
- Cell W ได้: $-u/\Delta x$

**แต่!** เมื่อเขียนสมการสำหรับ Cell W:
- Cell W ได้: $+u/\Delta x$
- Cell WW ได้: $-u/\Delta x$

**สรุป:** $A_{PW} \neq A_{WP}$ → **Asymmetric Matrix!**

**เทียบกับ Diffusion:**
$$\Gamma \frac{\partial^2 \phi}{\partial x^2} \approx \Gamma \frac{\phi_E - 2\phi_P + \phi_W}{\Delta x^2}$$

ที่นี่ $A_{PW} = A_{WP} = \Gamma/\Delta x^2$ → **Symmetric!**

</details>

<details>
<summary><b>Q2: ทำไม Implicit time scheme (Euler) ถึง "Unconditionally Stable"?</b></summary>

**คำตอบ:**

พิจารณา ODE: $\frac{d\phi}{dt} = -\lambda \phi$ (decay equation)

**Explicit Euler:**
$$\phi^{n+1} = \phi^n - \lambda \Delta t \cdot \phi^n = (1 - \lambda \Delta t) \phi^n$$

**Amplification factor:** $G = 1 - \lambda \Delta t$

- ถ้า $\lambda \Delta t > 2$ → $|G| > 1$ → **Unstable!**

**Implicit Euler:**
$$\phi^{n+1} = \phi^n - \lambda \Delta t \cdot \phi^{n+1}$$
$$\phi^{n+1} = \frac{\phi^n}{1 + \lambda \Delta t}$$

**Amplification factor:** $G = \frac{1}{1 + \lambda \Delta t}$

- สำหรับ $\lambda > 0$, **ไม่ว่า $\Delta t$ ใหญ่แค่ไหน** → $|G| < 1$ → **Always Stable!**

**ข้อแลก:** Implicit ต้องแก้สมการ (solve), Explicit ไม่ต้อง

</details>

<details>
<summary><b>Q3: "Diagonal Dominance" คืออะไร และทำไมสำคัญกับ Linear Solver?</b></summary>

**คำตอบ:**

**Diagonal Dominance:** $|a_{ii}| \geq \sum_{j \neq i} |a_{ij}|$ สำหรับทุกแถว

**ทำไมสำคัญ:**

1. **Iterative Solver Convergence:** Gauss-Seidel, Jacobi ต้องมี diagonal dominance
2. **Stability:** Matrix ที่ diagonal dominant มักจะ well-conditioned

**ใน OpenFOAM:**
- `fvm::ddt(U)` เพิ่ม $\frac{V}{\Delta t}$ ใน diagonal → ช่วย diagonal dominance
- ถ้า $\Delta t$ ใหญ่มาก → diagonal term เล็ก → อาจเสีย diagonal dominance → Solver ไม่ converge

**นี่คือสาเหตุที่:** ลด $\Delta t$ มักช่วยให้ simulation เสถียรขึ้น!

</details>

### Level 2: Deep Understanding

<details>
<summary><b>Q4: ทำไม "Bounded" scheme สำคัญสำหรับ Turbulence variables (k, ε)?</b></summary>

**คำตอบ:**

**Physical Constraint:**
- $k$ (turbulent kinetic energy) ต้อง $\geq 0$ เสมอ (พลังงานจลน์ไม่เป็นลบ)
- $\varepsilon$ (dissipation rate) ต้อง $> 0$ (ถ้า = 0, $\nu_t = C_\mu k^2/\varepsilon$ → หารด้วยศูนย์!)

**ปัญหา Unbounded scheme (linear):**
- สามารถ overshoot/undershoot → ค่าติดลบได้!
- ถ้า $k < 0$ → solver จะคำนวณ $\sqrt{k}$ ไม่ได้ → **Floating Point Error!**
- ถ้า $\varepsilon \leq 0$ → หารด้วยศูนย์ใน $\nu_t$ → **NaN → Blow up!**

**ทางออก:**
1. ใช้ `Gauss upwind` (bounded by design)
2. หรือ `Gauss limitedLinear 1` (bounded + 2nd order)
3. เพิ่ม `bound(k, 1e-10)` ใน code (safety net)

</details>

<details>
<summary><b>Q5: อธิบาย "Numerical Diffusion" ใน Upwind Scheme ด้วยการวิเคราะห์ Taylor Series</b></summary>

**คำตอบ:**

พิจารณา upwind discretization:
$$\left.\frac{\partial \phi}{\partial x}\right|_f \approx \frac{\phi_P - \phi_W}{\Delta x}$$

**Taylor Series ของ $\phi_W$ รอบ $x_P$:**
$$\phi_W = \phi_P - \Delta x \frac{\partial \phi}{\partial x} + \frac{(\Delta x)^2}{2} \frac{\partial^2 \phi}{\partial x^2} - O(\Delta x^3)$$

**แทนเข้าไป:**
$$\frac{\phi_P - \phi_W}{\Delta x} = \frac{\partial \phi}{\partial x} - \frac{\Delta x}{2} \frac{\partial^2 \phi}{\partial x^2} + O(\Delta x^2)$$

**Truncation Error:** $-\frac{\Delta x}{2} \frac{\partial^2 \phi}{\partial x^2}$

**นี่มีรูปแบบเหมือน Diffusion!** (Laplacian term)

**สรุป:** Upwind มี "false viscosity" ขนาด $\Gamma_{numerical} \approx \frac{u \Delta x}{2}$

**นี่คือเหตุผลที่:**
- ผลลัพธ์ดู "เบลอ" (smeared)
- Gradient ที่คมกลายเป็น smooth
- Mesh หยาบ → numerical diffusion สูงขึ้น

</details>

<details>
<summary><b>Q6: "Rhie-Chow Interpolation" คืออะไร และทำไมจำเป็นใน Colocated Grid?</b></summary>

**คำตอบ:**

**ปัญหา Colocated Grid:**

OpenFOAM เก็บ p และ U ที่ cell center เดียวกัน ("colocated")

**ปัญหา "Checkerboard":**
ถ้าใช้ central difference หา $\nabla p$:
$$\left.\frac{\partial p}{\partial x}\right|_P \approx \frac{p_E - p_W}{2\Delta x}$$

**สังเกต:** ไม่มี $p_P$ ในสมการ!

**ผลลัพธ์:** p สามารถมี pattern:
```
[100, 0, 100, 0, 100, 0]  ← Checkerboard!
```
แต่ $\nabla p = 0$ ทุกที่! → ผิด

**Rhie-Chow Interpolation:**
เพิ่ม pressure correction term เมื่อ interpolate velocity ไป face:
$$U_f = \overline{U} - \left(\overline{\frac{1}{a_P}}\right) \left(\nabla p|_f - \overline{\nabla p}\right)$$

**ผลลัพธ์:** pressure field ต้อง smooth ไม่งั้น face velocity จะผิด → ป้องกัน checkerboard!

</details>

### Level 3: Expert Understanding

<details>
<summary><b>Q7: ทำไม PISO ต้องมี "nCorrectors" มากกว่า 1? และค่าไหนเหมาะกับอะไร?</b></summary>

**คำตอบ:**

**กระบวนการ PISO:**

1. **Predictor:** แก้ momentum ด้วย p เก่า → ได้ $U^*$ (ไม่ satisfy continuity!)
2. **Corrector 1:** แก้ pressure equation → ได้ $p'$ → แก้ $U^* → U^{**}$
3. **Corrector 2+:** ทำซ้ำจนกว่า continuity error จะต่ำพอ

**ทำไมต้องมากกว่า 1?**

$p'$ ถูกคำนวณโดยสมมติว่า velocity ไม่เปลี่ยนมาก แต่จริงๆ เปลี่ยน!
→ ต้อง iterate

**Guidelines:**

| Courant | nCorrectors | เหตุผล |
|---------|-------------|--------|
| Co < 0.5 | 2 | Velocity เปลี่ยนน้อย, 2 รอบพอ |
| 0.5 < Co < 1 | 3 | เพิ่มความแม่นยำ |
| Co > 1 | ใช้ PIMPLE แทน! | PISO ไม่ designed สำหรับ Co > 1 |

**Test:** เพิ่ม `nCorrectors` แล้วดู `continuity error` ใน log — ถ้าไม่ลดลงแปลว่าพอแล้ว

</details>

<details>
<summary><b>Q8: "Under-Relaxation" ทำงานอย่างไรในระดับ Matrix?</b></summary>

**คำตอบ:**

**สมการเดิม:** $A\phi = b$

**ใส่ Under-Relaxation $\alpha$:**

แปลงเป็น:
$$\frac{A}{\alpha}\phi = b + \frac{1-\alpha}{\alpha}A_{diag}\phi^{old}$$

**ผลลัพธ์:**
- Diagonal coefficients เพิ่มขึ้น $\frac{1}{\alpha}$ เท่า → **Diagonal更 dominant**
- ค่าใหม่ = ผสมระหว่างค่าเก่ากับ solution

**มุมมองอีกแบบ:**
$$\phi^{new} = \alpha \cdot \phi^{solved} + (1-\alpha) \cdot \phi^{old}$$

**Field URF vs Equation URF:**

| Type | ใช้กับ | Effect |
|------|--------|--------|
| **fields** (p 0.3) | Apply หลัง solve | เปลี่ยน field โดยตรง |
| **equations** (U 0.7) | Apply ก่อน solve | แก้ matrix (ดีกว่า) |

**Stability Analysis:**
ถ้า URF ต่ำเกินไป → converge ช้ามาก
ถ้า URF สูงเกินไป → oscillate → diverge

**Rule of thumb:**
- p: 0.3 (sensitive มาก)
- U, k, ε: 0.7

</details>

<details>
<summary><b>Q9: อธิบาย "Deferred Correction" ใน OpenFOAM และทำไมใช้ใน Limited Schemes</b></summary>

**คำตอบ:**

**ปัญหา High-Order Schemes:**
Central Difference (linear) เป็น 2nd order แต่อาจ unbounded → coefficient ติดลบ → ทำลาย diagonal dominance

**Deferred Correction Approach:**

แทนที่จะใส่ high-order scheme ใน matrix โดยตรง:

1. **Implicit part:** ใช้ upwind (bounded, stable) → matrix A
2. **Explicit part:** เพิ่ม correction term: $(H.O. - upwind)$ → RHS

$$A\phi = b + (\text{High-order flux} - \text{Upwind flux})^{old}$$

**ข้อดี:**
- Matrix ยังคง well-conditioned (upwind-like diagonal dominance)
- ได้ accuracy ของ high-order scheme (เมื่อ converge)

**ใน OpenFOAM:**
`Gauss linearUpwind grad(U)` ใช้ deferred correction:
- Upwind ใส่ใน matrix
- Linear + gradient correction เป็น explicit

**สังเกตใน fvSchemes:**
```cpp
div(phi,U) Gauss linearUpwind grad(U);
//                              ↑ gradiend used for deferred correction
```

</details>

---

## 13. ⚡ Advanced Hands-on Challenges

> **คำเตือน:** Challenges เหล่านี้ต้องใช้เวลาและความเข้าใจลึก

### Challenge 1: Scheme Comparison Study (⭐⭐⭐)

**วัตถุประสงค์:** เห็นความแตกต่างระหว่าง schemes ด้วยตาตัวเอง

**Setup:**
```bash
# Clone pitzDaily tutorial
run
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily pitzDaily_upwind
cp -r pitzDaily_upwind pitzDaily_linear
cp -r pitzDaily_upwind pitzDaily_linearUpwind
```

**Tasks:**

1. **แก้ไข divSchemes ในแต่ละ case:**
   ```cpp
   // pitzDaily_upwind
   div(phi,U) Gauss upwind;
   
   // pitzDaily_linear
   div(phi,U) Gauss linear;
   
   // pitzDaily_linearUpwind
   div(phi,U) Gauss linearUpwind grad(U);
   ```

2. **รันและสังเกต:**
   - Case ไหน converge เร็วที่สุด?
   - Case ไหนระเบิด (ถ้ามี)?
   - เปรียบเทียบ velocity profile ที่ x/H = 5

3. **วิเคราะห์ผลลัพธ์:**
   - ทำไม `linear` (ถ้าไม่ระเบิด) ให้ recirculation zone ยาวกว่า `upwind`?
   - อธิบายด้วยทฤษฎี numerical diffusion

**Expected Learning:**
- เห็นว่า upwind "กลืน" recirculation ด้วย numerical diffusion
- เห็นความไม่เสถียรของ linear ใน high gradient region

---

### Challenge 2: Grid Convergence Study with Scheme Analysis (⭐⭐⭐⭐)

**วัตถุประสงค์:** เข้าใจความสัมพันธ์ระหว่าง mesh และ scheme

**Setup:**
```bash
# Use cavity tutorial
run
cp -r $FOAM_TUTORIALS/incompressible/icoFoam/cavity/cavity cavity_20
cp -r cavity_20 cavity_40
cp -r cavity_20 cavity_80
```

**Tasks:**

1. **สร้าง mesh 3 ระดับ:**
   ```cpp
   // cavity_20: 20x20
   // cavity_40: 40x40
   // cavity_80: 80x80
   ```

2. **รันแต่ละ case ด้วย `upwind` และ `linear`:**
   - รวม 6 simulations

3. **วัดค่า:**
   - Velocity ที่ center (0.05, 0.05, 0.005)
   - คำนวณ Grid Convergence Index (GCI)

4. **คำถามวิเคราะห์:**
   - Scheme ไหนมี observed order of accuracy ตรง theoretical มากกว่า?
   - ที่ mesh หยาบ (20x20), `upwind` หรือ `linear` ให้ผลใกล้ analytical solution มากกว่า?
   - อธิบายทำไม?

---

### Challenge 3: Custom P-V Coupling Investigation (⭐⭐⭐⭐⭐)

**วัตถุประสงค์:** เข้าใจ PISO/PIMPLE ในระดับ implementation

**Setup:**
```bash
# Use pimpleFoam tutorial
run
cp -r $FOAM_TUTORIALS/incompressible/pimpleFoam/laminar/movingCone movingCone_piso
cp -r movingCone_piso movingCone_pimple
```

**Tasks:**

1. **ตั้งค่า PISO-like:**
   ```cpp
   PIMPLE
   {
       nOuterCorrectors 1;  // เหมือน PISO
       nCorrectors 2;
   }
   ```

2. **ตั้งค่า PIMPLE:**
   ```cpp
   PIMPLE
   {
       nOuterCorrectors 3;
       nCorrectors 2;
   }
   ```

3. **ทดสอบ Courant Number:**
   - เริ่มด้วย Co = 0.5 → ทั้งสองน่าจะ stable
   - เพิ่มเป็น Co = 2 → ดูว่า case ไหนยังทำงานได้

4. **วิเคราะห์:**
   - Plot `continuity error` vs time สำหรับแต่ละ case
   - อธิบายว่า outer correctors ช่วยอย่างไร

---

### Challenge 4: Write Your Own Verification Test (⭐⭐⭐⭐⭐)

**วัตถุประสงค์:** เข้าใจ Numerical Verification ลึกซึ้ง

**Analytical Solution:**
ใช้ Couette Flow (flow between two parallel plates):

$$u(y) = U_{top} \frac{y}{H}$$

**Tasks:**

1. **สร้าง case:**
   - 2D channel, H = 0.1 m
   - Top wall: moving at U = 1 m/s
   - Bottom wall: stationary

2. **รัน 3 Mesh Levels:**
   - 5, 10, 20 cells in y-direction

3. **คำนวณ Error:**
   ```python
   L2_error = sqrt(sum((U_numerical - U_analytical)^2) / N)
   ```

4. **Plot log(error) vs log(h):**
   - Slope ควรเป็นเท่าไหร่สำหรับ 2nd order scheme?
   - ได้เท่าไหร่จริง?

5. **ทดสอบกับ mesh เบี้ยว:**
   - ใช้ `grading` ใน blockMesh
   - Order of accuracy เปลี่ยนไหม?

---

### Challenge 5: Investigate Relaxation Factor Sensitivity (⭐⭐⭐)

**วัตถุประสงค์:** เข้าใจ stability และ convergence tradeoff

**Setup:**
```bash
run
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/motorBike motorBike_base
```

**Tasks:**

1. **ตั้งค่า baseline:**
   ```cpp
   relaxationFactors { fields { p 0.3; } equations { U 0.7; } }
   ```

2. **ทดสอบ aggressive:**
   ```cpp
   relaxationFactors { fields { p 0.5; } equations { U 0.9; } }
   ```

3. **ทดสอบ conservative:**
   ```cpp
   relaxationFactors { fields { p 0.1; } equations { U 0.5; } }
   ```

4. **วัด:**
   - จำนวน iterations ถึง convergence
   - มี oscillation ใน residual plot ไหม?

5. **หา optimal:**
   - ค่าไหนที่ balance ระหว่าง stability และ speed?

---

## 14. ❌ Common Mistakes และ Solutions

### Mistake 1: ใช้ `linear` กับ Turbulence Variables

```cpp
// ❌ WRONG - จะระเบิด!
div(phi,k)       Gauss linear;
div(phi,epsilon) Gauss linear;

// ✅ CORRECT
div(phi,k)       Gauss upwind;        // หรือ limitedLinear 1
div(phi,epsilon) Gauss upwind;
```

**ทำไมผิด:** k และ ε ต้องเป็น positive เสมอ Linear scheme สามารถให้ค่าติดลบได้ → NaN → Crash

---

### Mistake 2: ลืม gradient scheme สำหรับ linearUpwind

```cpp
// ❌ WRONG - จะ error หรือใช้ผิด scheme
div(phi,U) Gauss linearUpwind;

// ✅ CORRECT
div(phi,U) Gauss linearUpwind grad(U);
```

**ทำไมผิด:** `linearUpwind` ต้องการ gradient ในการ reconstruct face value ถ้าไม่ระบุ OpenFOAM จะใช้ default ที่อาจไม่เหมาะสม

---

### Mistake 3: ใช้ `relTol 0` กับ SIMPLE

```cpp
// ❌ WRONG สำหรับ SIMPLE
p { solver PCG; tolerance 1e-6; relTol 0; }

// ✅ CORRECT สำหรับ SIMPLE
p { solver PCG; tolerance 1e-6; relTol 0.01; }

// ✅ CORRECT สำหรับ PISO/PIMPLE (transient)
p { solver PCG; tolerance 1e-6; relTol 0; }
```

**ทำไมผิด:** 

- **SIMPLE:** ทุก iteration ไม่ต้องแม่นยำ แค่ให้ทิศทางถูก → `relTol 0.01-0.1` ช่วยประหยัดเวลา
- **PISO:** ทุก time step ต้องแม่นยำ → `relTol 0` บังคับให้แก้จน tolerance

---

### Mistake 4: Non-orthogonal mesh โดยไม่เพิ่ม correctors

```bash
# checkMesh output
Mesh non-orthogonality Max: 75.2 degrees
```

```cpp
// ❌ WRONG - mesh เบี้ยวแต่ไม่มี correction
SIMPLE
{
    nNonOrthogonalCorrectors 0;
}

// ✅ CORRECT
SIMPLE
{
    nNonOrthogonalCorrectors 2;  // หรือ 3 ถ้าเบี้ยวมาก
}
```

**ทำไมผิด:** Non-orthogonal mesh ทำให้ gradient calculation เพี้ยน ต้อง iterate เพื่อแก้ไข

---

### Mistake 5: Courant Number สูงกับ PISO

```cpp
// ❌ WRONG - Co > 1 กับ PISO
deltaT 0.01;  // ทำให้ Co = 2

PISO
{
    nCorrectors 2;
}

// ✅ CORRECT - ใช้ PIMPLE แทน
PIMPLE
{
    nOuterCorrectors 2;  // ช่วย stability
    nCorrectors 2;
}
```

**ทำไมผิด:** PISO assume ว่า velocity field ไม่เปลี่ยนมากระหว่าง iteration ถ้า Co > 1 assumption นี้ผิด

---

### Mistake 6: ไม่ตรวจ log file อย่างละเอียด

```bash
# ❌ WRONG - ดูแค่ว่าจบหรือยัง
simpleFoam > log 2>&1 &
# (รอจนจบ แล้วดู ParaView)

# ✅ CORRECT - monitor ตลอด
tail -f log | grep -E "Residual|Courant|continuity"
```

**ควรเฝ้าดู:**
- Initial residual ลงเรื่อยๆ หรือไม่
- Continuity error อยู่ใน acceptable range หรือไม่ (< 1e-6)
- มี warning หรือ error หรือไม่

---

### Mistake 7: Copy-paste BCs โดยไม่เข้าใจ

```cpp
// ❌ WRONG - inlet ใช้ zeroGradient (ไม่ให้ข้อมูลอะไรเลย)
inlet
{
    type    zeroGradient;
}

// ✅ CORRECT - ต้องกำหนดค่า
inlet
{
    type    fixedValue;
    value   uniform (1 0 0);
}
```

**ทำไมผิด:** การเลือก BC ต้องตรงกับ physics:
- **Inlet:** ต้องกำหนดค่า (Dirichlet)
- **Outlet:** ปล่อยให้คำนวณ (Neumann/zeroGradient)
- **Wall:** no-slip สำหรับ velocity, zeroGradient สำหรับ pressure

---

### Mistake 8: snGradSchemes ไม่ตรงกับ laplacianSchemes

```cpp
// ❌ INCONSISTENT
laplacianSchemes { default Gauss linear corrected; }
snGradSchemes { default uncorrected; }  // ไม่ consistent!

// ✅ CONSISTENT
laplacianSchemes { default Gauss linear corrected; }
snGradSchemes { default corrected; }
```

**ทำไมผิด:** `laplacianSchemes` ใช้ `snGrad` internally ถ้าไม่ตรงกันจะเกิดความไม่สอดคล้อง → อาจ error หรือ inconsistent accuracy

---

## 15. 🔗 เชื่อมโยงกับ Repository

### อ่านเพิ่มเติม:

| หัวข้อ | ไฟล์ใน Repository |
|--------|-------------------|
| **fvc vs fvm ลึกขึ้น** | `MODULE_05/10_VECTOR_CALCULUS/02_fvc_vs_fvm.md` |
| **Discretization Theory** | `MODULE_01/01_GOVERNING_EQUATIONS/` |
| **SIMPLE Algorithm** | `MODULE_03/03_PRESSURE_VELOCITY_COUPLING/` |
| **Turbulence Modeling** | `MODULE_03/02_TURBULENCE_MODELING/` |
| **Matrix Solvers** | `MODULE_05/06_MATRICES_LINEARALGEBRA/` |
| **Mesh Quality** | `MODULE_02/02_SNAPPYHEXMESH/` |

---

*"ความเข้าใจที่แท้จริงมาจากการทำผิดและแก้ไขซ้ำแล้วซ้ำเล่า"*