# แนวคิดพื้นฐาน FVM

Finite Volume Method แบ่งโดเมนเป็น **Control Volumes (Cells)** และใช้หลักการอนุรักษ์กับแต่ละ Cell

> **ทำไมต้องใช้ FVM?**
> - **Conservation guarantee:** Flux ที่ออกจาก Cell A = Flux ที่เข้า Cell B → มวล/พลังงานไม่หาย
> - **Unstructured mesh:** รองรับ geometry ซับซ้อน
> - **Physical intuition:** สมการมาจากการ balance flux → เข้าใจง่าย

---

## หลักการ Control Volume

### Flux Balance

> **💡 คิดแบบนี้:**
> สมมติ Cell คือกล่องใส่น้ำ — ปริมาณน้ำในกล่องเปลี่ยนแปลงได้จาก 2 ทาง:
> 1. น้ำไหลเข้า/ออกผ่านผนัง (Flux)
> 2. มีก๊อกน้ำเปิด/ปิดในกล่อง (Source)

<!-- IMAGE: IMG_01_001 -->
<!-- 
Purpose: เพื่อแสดงหัวใจสำคัญของ FVM: การมองของไหลเป็น "ก้อนปริมาตรคงที่" (Control Volume) ที่มีกฎการอนุรักษ์ (Conservation Law) ควบคุมอยู่ โดยแสดงให้เห็นชัดเจนว่าปริมาณทางฟิสิกส์ (phi) เปลี่ยนแปลงได้จากการ "ไหลผ่านผิว" (Flux) และ "การเกิดภายใน" (Source) เท่านั้น ซึ่งต่างจากจุด (Node) ใน FDM
Prompt: "Engineering Diagram of a Finite Volume Control Cell. **Geometry:** A single isometric wireframe cube (black lines). **Elements:** 1. A central point labeled 'P' (Cell Center). 2. A point on the right face labeled 'f' (Face Center). 3. A straight arrow piercing the right face from inside to outside, labeled 'J_out' (Efflux). 4. A straight arrow entering the left face, labeled 'J_in' (Influx). 5. A normal vector arrow perpendicular to the face, labeled 'Sf'. **Style:** Technical textbook line art, white background, black lines, minimal color (only blue for flux arrows), clear mathematical labels (LaTeX style). No glowing effects, no abstract fluid."
-->
![IMG_01_001: Control Volume Conservation Concept.jpg](IMG_01_001.jpg)

สำหรับแต่ละ Cell:

$$\underbrace{\frac{d}{dt}\int_V \phi\, dV}_{\text{สะสมในกล่อง}} + \underbrace{\sum_f \mathbf{F}_f \cdot \mathbf{S}_f}_{\text{ไหลออกผ่านผนัง}} = \underbrace{\int_V S\, dV}_{\text{ผลิต/บริโภค}}$$

**ทำไม FVM อนุรักษ์โดยอัตโนมัติ?**
- Flux ที่ Face ถูกคำนวณ **ครั้งเดียว** และใช้ร่วมกันระหว่าง 2 Cells ที่อยู่ติดกัน
- สิ่งที่ไหลออกจาก Cell A จะเข้า Cell B พอดี → ไม่มีการสร้างหรือทำลาย

---

### Cell-Centered Storage

**ปัญหา:** เราเก็บค่า ($\phi$) ที่ Cell Center แต่ต้องคำนวณ Flux ที่ Face

<!-- IMAGE: IMG_01_002 -->
<!-- 
Purpose: เพื่อชี้ให้เห็น "ปัญหาหลัก" ของ FVM แบบ Cell-Centered: ข้อมูลเก็บอยู่ที่ "จุดศูนย์กลาง" (Cell Center) แต่สมการต้องการค่าที่ "ผิว" (Face) เพื่อคำนวณ Flux. ภาพนี้ต้องสื่อว่าค่าที่ Face ($\phi_f$) คือ "Unknown" ที่เราต้องหาทางประมาณค่าขึ้นมา (Interpolation)
Prompt: "2D Engineering Schematic of Finite Volume Discretization. **Geometry:** Two perfect square cells touching side-by-side. Left square is 'Cell P', Right square is 'Cell N'. **Elements:** 1. A blue dot in the exact center of Cell P labeled 'φ_P'. 2. A blue dot in the exact center of Cell N labeled 'φ_N'. 3. A red 'X' or hollow circle on the shared vertical line between the squares labeled 'φ_f = ?'. 4. A dashed line connecting the two blue dots. 5. A small arrow pointing from left to right across the boundary labeled 'Sf'. **Style:** Flat 2D technical drawing, black outlines on white background, no shading, no 3D, clear LaTeX-style labels."
-->
![IMG_01_002: The Face Interpolation Problem](IMG_01_002.jpg)

**ทางออก:** ใช้ **Interpolation Schemes** เพื่อ "เดา" ค่าที่ Face จากค่าที่ Cell Centers

| ตัวแปร | ความหมาย | ทำไมสำคัญ |
|--------|----------|----------|
| $V_P$ | Cell Volume | ใช้คำนวณ accumulation term |
| $\mathbf{S}_f$ | Face Area Vector | ใช้คำนวณ flux ผ่าน face |
| $\mathbf{d}_{PN}$ | ระยะห่าง P→N | ใช้คำนวณ gradient |

**OpenFOAM Access:**
```cpp
mesh.V()      // Cell volumes
mesh.Sf()     // Face area vectors
mesh.delta()  // Cell-to-cell distances
```

---

## สมการอนุรักษ์

### 1. Mass (Continuity)

$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$$

**Incompressible:** $\nabla \cdot \mathbf{u} = 0$

**ทำไมสมการนี้สำคัญ?**
- ไม่ใช่แก้หามวล แต่ใช้เป็น **constraint** สร้างสมการ pressure
- ถ้า divergence ไม่เป็นศูนย์ = มวลหายไป → ผลลัพธ์ผิด

**OpenFOAM:** บังคับผ่าน pressure correction (SIMPLE/PISO)

---

### 2. Momentum (Navier-Stokes)

$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

**แต่ละ term หมายความว่าอะไร?**

| พจน์ | ชื่อ | ความหมายทางกายภาพ | OpenFOAM |
|------|------|-------------------|----------|
| $\rho \partial\mathbf{u}/\partial t$ | Local acceleration | ความเร็วเปลี่ยนตามเวลา ณ จุดเดิม | `fvm::ddt(rho, U)` |
| $\rho (\mathbf{u} \cdot \nabla) \mathbf{u}$ | Convection | ของไหลพาโมเมนตัมไปด้วย (ทำให้ nonlinear!) | `fvm::div(phi, U)` |
| $-\nabla p$ | Pressure force | ความดันดันจากสูงไปต่ำ | `fvc::grad(p)` |
| $\mu \nabla^2 \mathbf{u}$ | Viscous force | ความหนืดยับยั้งการไหล (ทำให้เสถียร) | `fvm::laplacian(mu, U)` |

**ทำไม Convection term ถึงยาก?**
- มี $\mathbf{u}$ คูณ $\mathbf{u}$ → **Nonlinear**
- ค่าอาจกระโดดมาก → ต้องใช้ scheme ที่เสถียร (upwind)

---

### 3. Energy

$$\rho c_p \frac{\partial T}{\partial t} + \rho c_p \mathbf{u} \cdot \nabla T = k \nabla^2 T + Q$$

**ใช้เมื่อไหร่?**
- ❌ น้ำไหลในท่อที่อุณหภูมิคงที่ → ไม่ต้องแก้
- ✅ Heat transfer → ต้องแก้
- ✅ Compressible flow → ต้องแก้ เพราะ ρ ขึ้นกับ T

**OpenFOAM Files:**
- `0/T` หรือ `0/h` (enthalpy)
- `constant/thermophysicalProperties`

---

## Pressure-Velocity Coupling

> **ปัญหา "งูกินหาง":**
> - สมการ Momentum ต้องใช้ $p$ → แต่ $p$ มาจากไหน?
> - สมการ Continuity บังคับให้ $\nabla \cdot \mathbf{u} = 0$ → ใช้สร้างสมการ $p$
> - แต่สมการ $p$ ต้องใช้ $\mathbf{u}$!

**ทางออก:** ใช้ **Iterative Algorithm**

| Algorithm | ใช้เมื่อ | หลักการ |
|-----------|---------|---------|
| **SIMPLE** | Steady-state | วนซ้ำจนนิ่ง ใช้ under-relaxation |
| **PISO** | Transient, Δt เล็ก | แก้ pressure หลายรอบต่อ time step |
| **PIMPLE** | Transient, Δt ใหญ่ | รวม SIMPLE + PISO (outer + inner loops) |

**การตั้งค่าใน `system/fvSolution`:**

```cpp
// Steady-state
SIMPLE
{
    nNonOrthogonalCorrectors 1;  // แก้ mesh เบี้ยว
    residualControl { p 1e-4; U 1e-4; }
}

// Transient
PIMPLE
{
    nOuterCorrectors 2;   // SIMPLE-like outer loop
    nCorrectors 1;        // PISO-like inner loop
}
```

---

## General Transport Equation

**ทุกสมการอนุรักษ์เขียนได้ในรูปเดียวกัน:**

$$\underbrace{\frac{\partial \phi}{\partial t}}_{\text{เวลา}} + \underbrace{\nabla \cdot (\mathbf{u}\phi)}_{\text{พา (Convection)}} = \underbrace{\nabla \cdot (D \nabla \phi)}_{\text{กระจาย (Diffusion)}} + \underbrace{S}_{\text{แหล่ง}}$$

**ทำไมรูปนี้สำคัญ?**
- OpenFOAM ใช้รูปนี้เป็นพื้นฐานในการ discretize ทุกสมการ
- เข้าใจรูปนี้ = เข้าใจทุก solver

**OpenFOAM Implementation:**

```cpp
fvScalarMatrix phiEqn
(
    fvm::ddt(phi)              // ∂φ/∂t
  + fvm::div(phi, U)           // ∇·(uφ)
  - fvm::laplacian(D, phi)     // ∇·(D∇φ)
 ==
    Su                         // S
);
phiEqn.solve();
```

> **💡 ความแตกต่าง fvm:: vs fvc:::**
>
> | Prefix | ชื่อเต็ม | การใช้งาน | ผลลัพธ์ |
> |--------|-----------|-------------|---------|
> | `fvm::` | Finite Volume Matrix | **Implicit** — สำหรับ unknowns | สร้าง matrix coefficients → แก้ด้วย linear solver |
> | `fvc::` | Finite Volume Calculated | **Explicit** — สำหรับ knowns | คำนวณค่าทันที → ใช้เป็น source term |
>
> **กฎง่ายๆ:**
> - ถ้าตัวแปร **กำลังจะหา** (เช่น U, p ใน iteration นี้) → ใช้ `fvm::`
> - ถ้าตัวแปร **รู้ค่าแล้ว** (เช่น p จาก iteration ก่อนหน้า) → ใช้ `fvc::`
> - `fvm::` ทำให้ matrix **ใหญ่ขึ้น** แต่ **stable กว่า**
> - `fvc::` ทำให้ compute **เร็วกว่า** แต่ **ต้องลด Δt**

---

## Files ที่เกี่ยวข้อง

| Location | เนื้อหา | ทำไมสำคัญ |
|----------|---------|----------|
| `constant/polyMesh/` | Mesh (cells, faces, points) | กำหนดรูปร่างโดเมน |
| `constant/transportProperties` | ν, ρ, μ | กำหนดคุณสมบัติของไหล |
| `constant/turbulenceProperties` | Turbulence model | เลือก k-ε, k-ω ฯลฯ |
| `0/` | Initial & BCs | ค่าเริ่มต้น + ขอบเขต |
| `system/fvSchemes` | Discretization | เลือก upwind/linear |
| `system/fvSolution` | Solver settings | เลือก SIMPLE/PISO |

---

## Concept Check

<details>
<summary><b>1. ทำไม FVM ถึง "อนุรักษ์" โดยธรรมชาติ?</b></summary>

เพราะ Flux ที่ Face คำนวณ **ครั้งเดียว** และใช้ร่วมกันระหว่าง 2 Cells → สิ่งที่ออกจาก Cell A จะเข้า Cell B พอดี ไม่มีการสร้างหรือทำลาย

**เปรียบเทียบ:** เหมือนระบบน้ำในท่อที่เชื่อมต่อกัน — น้ำที่ออกจากท่อ A ต้องเข้าท่อ B เสมอ
</details>

<details>
<summary><b>2. ในสมการโมเมนตัม ทำไม pressure gradient ใช้ fvc ไม่ใช่ fvm?</b></summary>

เพราะ $-\nabla p$ ไม่มี $\mathbf{u}$ อยู่ในนั้น:
- **fvm::** ใช้กับ **unknown** (เช่น U ที่กำลังหา) → ใส่ใน matrix
- **fvc::** ใช้กับ **known** (เช่น p จาก iteration ก่อน) → คำนวณเป็นตัวเลข

p มาจาก pressure correction ที่แยกต่างหาก จึงเป็น known value
</details>

<details>
<summary><b>3. SIMPLE กับ PISO ต่างกันอย่างไร?</b></summary>

| | SIMPLE | PISO |
|-|--------|------|
| **ใช้กับ** | Steady-state | Transient |
| **วิธีการ** | วนซ้ำจนลู่เข้า | แก้ p หลายครั้ง/time step |
| **Under-relaxation** | ต้องใช้ (0.3-0.7) | ไม่ต้อง |
| **ทำไม** | ไม่สน intermediate → รอ converge | ทุก step ต้องแม่น |
</details>

<details>
<summary><b>4. Convection term ทำไมถึง "ยาก" ที่สุดในการ discretize?</b></summary>

1. **Nonlinear:** มี $u \cdot u$ → ต้องวนซ้ำ (iterate)
2. **Unbounded:** ค่าอาจกระโดดสูงมาก → oscillation → blow up
3. **Directional:** ข้อมูลไหลตามทิศทางลม → ต้องคิดเรื่อง upwind/downwind
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_Introduction.md](01_Introduction.md) — บทนำ FVM
- **บทถัดไป:** [03_Spatial_Discretization.md](03_Spatial_Discretization.md) — Spatial Discretization
- **ประยุกต์ใช้:** [06_OpenFOAM_Implementation.md](06_OpenFOAM_Implementation.md) — การ implement ใน OpenFOAM