# บทนำสู่ Finite Volume Method

**Finite Volume Method (FVM)** เป็นวิธี discretization ที่ OpenFOAM ใช้แปลง PDE ให้เป็นระบบสมการพีชคณิต

---

## แนวคิดหลัก

### จาก PDE สู่ Algebraic Equations

สมการอนุรักษ์ทั่วไป:

$$\frac{\partial \phi}{\partial t} + \nabla \cdot \mathbf{F}(\phi) = S(\phi)$$

FVM ทำการ:
1. **แบ่งโดเมน** เป็น Control Volumes (Cells)
2. **Integrate** สมการเหนือแต่ละ Cell
3. **ใช้ Gauss Theorem** แปลง Volume Integral → Surface Integral
4. **สร้างสมการพีชคณิต** สำหรับแต่ละ Cell

$$\int_V \frac{\partial \phi}{\partial t} dV + \oint_S \mathbf{F} \cdot \mathbf{n}\, dS = \int_V S\, dV$$

### ข้อดีของ FVM

| ข้อดี | เหตุผล |
|------|--------|
| **Conservation** | Flux ที่ออกจาก Cell A = Flux ที่เข้า Cell B |
| **Flexibility** | รองรับ Unstructured, Polyhedral Mesh |
| **Physical Intuition** | ตีความได้ว่าเป็น "สมดุลการไหล" |

---

## Control Volume Approach

### Cell-Centered Storage

ใน OpenFOAM ค่าตัวแปรเก็บที่ **Cell Center**:

```
Cell P ─── Face f ─── Cell N
  │           │           │
 φ_P         φ_f         φ_N
(known)   (interpolate) (known)
```

- **P** = Owner Cell
- **N** = Neighbor Cell
- **f** = Face ระหว่าง P กับ N
- **S_f** = Face Area Vector (ชี้จาก P ไป N)

### Flux Balance

สำหรับแต่ละ Cell:

$$\sum_f \mathbf{F}_f \cdot \mathbf{S}_f = 0$$

สิ่งที่ไหลเข้า = สิ่งที่ไหลออก (+ Sources)

---

## Discretization Process

### 1. Convective Term

$$\nabla \cdot (\phi \mathbf{u}) \rightarrow \sum_f \phi_f \Phi_f$$

โดย $\Phi_f = \mathbf{u}_f \cdot \mathbf{S}_f$ คือ volumetric flux

**Interpolation Schemes:**

| Scheme | สูตร | Order | เสถียรภาพ |
|--------|------|-------|-----------|
| Upwind | $\phi_f = \phi_P$ (ถ้า $\Phi_f > 0$) | 1 | สูง |
| Linear | $\phi_f = \frac{1}{2}(\phi_P + \phi_N)$ | 2 | ต่ำ |
| LimitedLinear | Linear + TVD limiter | 2 | กลาง |

### 2. Diffusive Term

$$\nabla \cdot (D \nabla \phi) \rightarrow \sum_f D_f \frac{\phi_N - \phi_P}{d_{PN}} |S_f|$$

สำหรับ Orthogonal Mesh เท่านั้น — Non-orthogonal ต้องมี correction

### 3. Temporal Term

$$\frac{\partial \phi}{\partial t} \rightarrow \frac{\phi^{n+1} - \phi^n}{\Delta t}$$

**Schemes:**

| Scheme | Order | ความเสถียร |
|--------|-------|-----------|
| Euler | 1 | ดีมาก |
| Backward | 2 | ดี |
| Crank-Nicolson | 2 | ปานกลาง |

---

## Matrix Assembly

หลังจาก discretize ทุก term จะได้สมการสำหรับแต่ละ Cell:

$$a_P \phi_P + \sum_N a_N \phi_N = b_P$$

รวมทุก Cell → ระบบสมการเชิงเส้น:

$$[A][\phi] = [b]$$

- **A** = Sparse Matrix (ส่วนใหญ่เป็น 0)
- **φ** = Unknown Values ที่ทุก Cell
- **b** = Source Terms + Boundary Contributions

---

## OpenFOAM Implementation

### Key Classes

| Class | หน้าที่ |
|-------|--------|
| `fvMesh` | เก็บ topology และ geometry |
| `volScalarField` | Field ที่ Cell Centers |
| `surfaceScalarField` | Field ที่ Faces (fluxes) |
| `fvMatrix` | ระบบสมการ [A][x]=[b] |

### Operators

| Operator | คณิตศาสตร์ | Type |
|----------|-----------|------|
| `fvm::ddt(phi)` | $\partial\phi/\partial t$ | Implicit |
| `fvm::div(phi, U)` | $\nabla \cdot (\phi \mathbf{U})$ | Implicit |
| `fvm::laplacian(D, phi)` | $\nabla \cdot (D \nabla \phi)$ | Implicit |
| `fvc::grad(p)` | $\nabla p$ | Explicit |
| `fvc::div(phi)` | $\nabla \cdot \phi$ | Explicit |

### ตัวอย่าง: Scalar Transport Equation

$$\frac{\partial T}{\partial t} + \nabla \cdot (\mathbf{u} T) = D \nabla^2 T$$

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T)               // ∂T/∂t
  + fvm::div(phi, T)          // ∇·(uT)
  - fvm::laplacian(D, T)      // -D∇²T
);

TEqn.solve();
```

---

## Files ที่เกี่ยวข้อง

| File | เนื้อหา |
|------|---------|
| `constant/polyMesh/` | Mesh topology |
| `0/` | Initial & Boundary Conditions |
| `system/fvSchemes` | Discretization Schemes |
| `system/fvSolution` | Linear Solvers |

---

## Concept Check

<details>
<summary><b>1. ทำไม FVM ถึง "อนุรักษ์" โดยธรรมชาติ?</b></summary>

เพราะ Flux ที่ Face f คำนวณครั้งเดียวและใช้ร่วมกันระหว่าง 2 Cells ดังนั้นสิ่งที่ออกจาก Cell หนึ่งจะเข้าอีก Cell หนึ่งพอดี ไม่มีการสูญหาย
</details>

<details>
<summary><b>2. Upwind vs Linear ต่างกันอย่างไร?</b></summary>

- **Upwind**: ใช้ค่าจาก upstream เท่านั้น → เสถียรแต่ diffusive
- **Linear**: เฉลี่ยทั้งสอง Cell → แม่นยำแต่อาจ oscillate
</details>

<details>
<summary><b>3. ถ้า Mesh ไม่ orthogonal จะเกิดอะไรขึ้น?</b></summary>

การคำนวณ Gradient ที่ Face จะมี error ต้องใช้ Non-orthogonal Correction (`nNonOrthogonalCorrectors > 0`) เพื่อแก้ไข
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [00_Overview.md](00_Overview.md) — ภาพรวม FVM
- **บทถัดไป:** [02_Fundamental_Concepts.md](02_Fundamental_Concepts.md) — Control Volume และ Mesh